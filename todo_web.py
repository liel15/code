import json
import os
import random
from datetime import datetime, timedelta

from flask import Flask, jsonify, render_template, request


app = Flask(__name__)
app.secret_key = "todo-secret"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "todos.json")
GAME_FILE = os.path.join(BASE_DIR, "game_state.json")


def load_todos():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_todos(todos):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(todos, f, ensure_ascii=False, indent=2)


def default_game_state():
    todos = normalize_todos(load_todos())
    completed_count = sum(1 for t in todos if t["completed"])
    return {
        "xp": completed_count * 50,
        "coins": completed_count * 10,
        "owned": [],
        "boosts": {"xp_uses": 0, "coin_uses": 0},
        "daily_claimed": None,
        "tree": default_tree_state(),
    }


def load_game_state():
    if not os.path.exists(GAME_FILE):
        return default_game_state()
    with open(GAME_FILE, "r", encoding="utf-8") as f:
        state = json.load(f)
    state.setdefault("xp", 0)
    state.setdefault("coins", 0)
    state.setdefault("owned", [])
    state.setdefault("boosts", {"xp_uses": 0, "coin_uses": 0})
    state.setdefault("daily_claimed", None)
    state.setdefault("tree", default_tree_state())
    state["boosts"].setdefault("xp_uses", 0)
    state["boosts"].setdefault("coin_uses", 0)
    normalize_tree_state(state["tree"])
    return state


def save_game_state(state):
    with open(GAME_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def default_tree_state():
    return {
        "hp": 100,
        "growth_bonus": 0,
        "free_water_date": None,
        "free_water_used": 0,
        "waterings_today": 0,
        "last_schedule_penalty_date": None,
        "dead": False,
        "grave": False,
        "death_reason": None,
        "background_items": ["초원"],
        "house": "나무집",
        "outfit": "새싹옷",
        "message": "새싹이 자라고 있어요.",
        "last_event": None,
        "harvest_count": 0,
        "harvested": False,
    }


def normalize_tree_state(tree):
    defaults = default_tree_state()
    for key, value in defaults.items():
        if key not in tree:
            tree[key] = value if not isinstance(value, list) else list(value)
    tree["hp"] = max(0, min(100, int(tree.get("hp", 100))))
    tree["growth_bonus"] = max(-100, min(100, int(tree.get("growth_bonus", 0))))
    tree["free_water_used"] = max(0, int(tree.get("free_water_used", 0)))
    tree["waterings_today"] = max(0, int(tree.get("waterings_today", 0)))
    tree["harvest_count"] = max(0, int(tree.get("harvest_count", 0)))
    return tree


def tree_health_label(hp):
    if hp <= 10:
        return "건조"
    if hp <= 40:
        return "배고픔"
    if hp <= 60:
        return "평온"
    if hp <= 80:
        return "배부름"
    return "건강함"


def compute_tree_growth(todos, tree):
    total = len(todos)
    completed = sum(1 for t in todos if t["completed"])
    schedule_progress = int((completed / total) * 100) if total else 0
    growth = min(100, schedule_progress + tree.get("growth_bonus", 0))
    stage = min(5, max(1, (growth // 20) + 1))
    return schedule_progress, growth, stage


def overdue_summary(todos):
    now = datetime.now()
    overdue_items = []
    for todo in todos:
        due = parse_due_datetime(todo.get("due_date"))
        if due and not todo["completed"] and due < now:
            overdue_items.append((todo, due))

    if not overdue_items:
        return 0, 0

    latest_overdue_days = 0
    for _, due in overdue_items:
        overdue_days = max(1, (now.date() - due.date()).days)
        latest_overdue_days = max(latest_overdue_days, overdue_days)

    return len(overdue_items), latest_overdue_days


def apply_overdue_penalty(tree, overdue_count, overdue_days, today):
    if overdue_count <= 0 or tree.get("dead"):
        return

    penalty_key = f"{today}:{overdue_count}:{overdue_days}"
    if tree.get("last_overdue_penalty_key") == penalty_key:
        return

    penalty = min(35, 6 + (overdue_count * 4) + (overdue_days * 2))
    tree["hp"] = max(0, tree["hp"] - penalty)
    tree["growth_bonus"] = max(-100, tree.get("growth_bonus", 0) - max(1, overdue_count))
    tree["last_overdue_penalty_key"] = penalty_key
    tree["last_schedule_penalty_date"] = today
    tree["last_event"] = f"마감 초과 {overdue_count}건으로 HP가 {penalty} 감소했어요."
    tree["health_label"] = tree_health_label(tree["hp"])
    tree["state_label"] = tree["health_label"]
    tree["message"] = "마감이 밀리면 HP가 줄어들어요."
    if tree["hp"] == 0:
        tree["dead"] = True
        tree["grave"] = True
        tree["death_reason"] = "일정 초과"
        tree["message"] = "일정을 지켜야 해요."


def sync_tree_state(todos, game_state):
    tree = game_state.setdefault("tree", default_tree_state())
    normalize_tree_state(tree)
    today = datetime.now().date().isoformat()

    if tree.get("free_water_date") != today:
        tree["free_water_date"] = today
        tree["free_water_used"] = 0
        tree["waterings_today"] = 0

    schedule_progress, growth, stage = compute_tree_growth(todos, tree)
    tree["schedule_progress"] = schedule_progress
    tree["growth"] = growth
    tree["stage"] = stage
    overdue_count, overdue_days = overdue_summary(todos)
    apply_overdue_penalty(tree, overdue_count, overdue_days, today)
    tree["health_label"] = tree_health_label(tree["hp"])
    tree["can_harvest"] = growth >= 100 and not tree["dead"] and not tree.get("harvested")
    tree["state_label"] = "죽음" if tree["dead"] else tree["health_label"]

    return tree


def next_id(todos):
    return (max((todo["id"] for todo in todos), default=0) + 1)


def normalize_todos(todos):
    for todo in todos:
        todo.setdefault("completed", False)
        todo.setdefault("priority", "medium")
        todo.setdefault("created_at", datetime.now().strftime("%Y-%m-%d %H:%M"))
        todo.setdefault("due_date", None)
        todo.setdefault("completed_at", None)
        todo.setdefault("note", "")
        todo.setdefault("tree_sold", False)
        todo.setdefault("tree_decorations", [])
    return todos


def parse_created_datetime(value):
    if not value:
        return datetime.min
    value = str(value).strip()
    try:
        return datetime.strptime(value, "%Y-%m-%d %H:%M")
    except ValueError:
        try:
            return datetime.fromisoformat(value.replace(" ", "T"))
        except ValueError:
            return datetime.min


def parse_due_datetime(value):
    if not value:
        return None
    value = str(value).strip()
    try:
        if len(value) == 10:
            return datetime.strptime(value, "%Y-%m-%d").replace(hour=23, minute=59)
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is not None:
            parsed = parsed.astimezone().replace(tzinfo=None)
        return parsed
    except ValueError:
        try:
            return datetime.strptime(value, "%Y-%m-%d %H:%M")
        except ValueError:
            return None


def format_due_datetime(value):
    due = parse_due_datetime(value)
    return due.strftime("%Y-%m-%d %H:%M") if due else "없음"


def humanize_timedelta(delta):
    total_minutes = max(0, int(abs(delta.total_seconds()) // 60))
    days, remainder = divmod(total_minutes, 1440)
    hours, minutes = divmod(remainder, 60)
    parts = []
    if days:
        parts.append(f"{days}일")
    if hours:
        parts.append(f"{hours}시간")
    if minutes and not days:
        parts.append(f"{minutes}분")
    return " ".join(parts) or "0분"


def due_meta(todo):
    due = parse_due_datetime(todo.get("due_date"))
    if not due:
        return {"exact": "없음", "status": "마감일 없음", "tone": "muted", "kind": "none"}

    now = datetime.now()
    delta = due - now
    exact = due.strftime("%Y-%m-%d %H:%M")
    if delta.total_seconds() < 0:
        return {
            "exact": exact,
            "status": f"{humanize_timedelta(delta)} 지남",
            "tone": "danger",
            "kind": "overdue",
        }
    if delta <= timedelta(days=7):
        return {
            "exact": exact,
            "status": "임박",
            "tone": "warning",
            "kind": "upcoming",
        }
    return {
        "exact": exact,
        "status": "예정",
        "tone": "info",
        "kind": "future",
    }


def tree_meta(todo):
    due = parse_due_datetime(todo.get("due_date"))
    now = datetime.now()
    if todo.get("tree_sold"):
        return {"emoji": "🪙", "label": "판매 완료", "tone": "secondary", "can_sell": False, "can_decorate": False}
    if todo.get("completed"):
        return {"emoji": "🌳", "label": "성장 완료", "tone": "success", "can_sell": True, "can_decorate": True}
    if due and due < now:
        return {"emoji": "🥀", "label": "시든 나무", "tone": "danger", "can_sell": False, "can_decorate": False}
    if due and due - now <= timedelta(days=7):
        return {"emoji": "🌱", "label": "자라는 나무", "tone": "warning", "can_sell": False, "can_decorate": True}
    return {"emoji": "🌿", "label": "건강한 나무", "tone": "info", "can_sell": False, "can_decorate": True}


def priority_label(priority):
    return {"high": "높음", "medium": "보통", "low": "낮음"}.get(priority, "보통")


def parse_date(value):
    return datetime.strptime(value, "%Y-%m-%d").date()


def parse_completed_dates(todos):
    dates = set()
    for todo in todos:
        completed_at = todo.get("completed_at")
        if completed_at:
            dates.add(datetime.strptime(completed_at, "%Y-%m-%d %H:%M").date())
    return dates


def calc_streak(completed_dates):
    streak = 0
    current = datetime.now().date()
    while current in completed_dates:
        streak += 1
        current = current - timedelta(days=1)
    return streak


def level_from_xp(xp):
    level = (xp // 200) + 1
    current = xp % 200
    return level, current, 200


def mission_template_for_today():
    today = datetime.now().date()
    templates = [
        {"kind": "complete", "title": "오늘 {target}개 완료", "reward": 80, "min": 1, "max": 3},
        {"kind": "note", "title": "메모 {target}개 작성", "reward": 70, "min": 1, "max": 3},
        {"kind": "add", "title": "할일 {target}개 추가", "reward": 60, "min": 1, "max": 2},
        {"kind": "high_complete", "title": "높음 우선순위 {target}개 완료", "reward": 100, "min": 1, "max": 2},
    ]
    idx = today.toordinal() % len(templates)
    item = templates[idx].copy()
    span = item["max"] - item["min"] + 1
    item["target"] = item["min"] + (today.toordinal() % span)
    item["date"] = today.isoformat()
    return item


def build_daily_mission(todos, game_state):
    mission = mission_template_for_today()
    today = datetime.now().date()
    completed_today = [t for t in todos if t["completed"] and t.get("completed_at") and datetime.strptime(t["completed_at"], "%Y-%m-%d %H:%M").date() == today]
    created_today = [t for t in todos if parse_date(t["created_at"][:10]) == today]
    note_count = sum(1 for t in todos if t.get("note"))
    high_completed = sum(1 for t in completed_today if t["priority"] == "high")

    if mission["kind"] == "complete":
        current = len(completed_today)
    elif mission["kind"] == "note":
        current = note_count
    elif mission["kind"] == "add":
        current = len(created_today)
    else:
        current = high_completed

    claimed = game_state.get("daily_claimed") == today.isoformat()
    return {
        "title": mission["title"].format(target=mission["target"]),
        "kind": mission["kind"],
        "target": mission["target"],
        "current": current,
        "reward": mission["reward"],
        "can_claim": current >= mission["target"] and not claimed,
        "claimed": claimed,
    }


def shop_items():
    return [
        {"id": "neon_aura", "name": "Neon Aura", "price": 120, "kind": "cosmetic", "desc": "화면을 더 화려하게 만듭니다."},
        {"id": "tree_lantern", "name": "Tree Lantern", "price": 90, "kind": "cosmetic", "desc": "나무에 장식을 달 수 있습니다."},
        {"id": "xp_boost", "name": "XP Booster", "price": 180, "kind": "boost", "desc": "다음 5회 완료 시 XP 2배."},
        {"id": "coin_crate", "name": "Coin Crate", "price": 150, "kind": "boost", "desc": "다음 5회 완료 시 코인 +10."},
    ]


def build_shop(game_state):
    owned = set(game_state.get("owned", []))
    boosts = game_state.get("boosts", {})
    items = []
    for item in shop_items():
        item = item.copy()
        if item["id"] == "xp_boost":
            item["owned"] = boosts.get("xp_uses", 0)
            item["label"] = f'{item["desc"]} ({boosts.get("xp_uses", 0)}회 남음)'
        elif item["id"] == "coin_crate":
            item["owned"] = boosts.get("coin_uses", 0)
            item["label"] = f'{item["desc"]} ({boosts.get("coin_uses", 0)}회 남음)'
        else:
            item["owned"] = item["id"] in owned
            item["label"] = item["desc"]
        items.append(item)
    return items


def apply_completion_reward(todo, game_state):
    xp_mult = 2 if game_state.get("boosts", {}).get("xp_uses", 0) > 0 else 1
    coin_bonus = 10 if game_state.get("boosts", {}).get("coin_uses", 0) > 0 else 0
    if game_state.get("boosts", {}).get("xp_uses", 0) > 0:
        game_state["boosts"]["xp_uses"] -= 1
    if game_state.get("boosts", {}).get("coin_uses", 0) > 0:
        game_state["boosts"]["coin_uses"] -= 1

    xp_gain = 50 * xp_mult
    coin_gain = 10 + coin_bonus
    if todo.get("priority") == "high":
        coin_gain += 5
    due = parse_due_datetime(todo.get("due_date"))
    if due and due < datetime.now():
        coin_gain += 5
    game_state["xp"] += xp_gain
    game_state["coins"] += coin_gain
    return xp_gain, coin_gain


def apply_tree_sale_reward(todo, game_state):
    reward = 40
    if todo.get("priority") == "high":
        reward += 10
    due = parse_due_datetime(todo.get("due_date"))
    if due and due < datetime.now():
        reward += 10
    game_state["coins"] += reward
    return reward


def build_gamification(todos):
    completed = [t for t in todos if t["completed"]]
    completed_count = len(completed)
    xp = completed_count * 50
    level = (xp // 200) + 1
    level_current = xp % 200
    level_target = 200
    streak = calc_streak(parse_completed_dates(todos))

    today = datetime.now().date()
    today_completed = sum(1 for t in completed if t.get("completed_at") and datetime.strptime(t["completed_at"], "%Y-%m-%d %H:%M").date() == today)
    today_created = sum(1 for t in todos if parse_date(t["created_at"][:10]) == today)

    badges = []
    if completed_count >= 1:
        badges.append({"name": "첫 승리", "icon": "⚔", "tone": "info"})
    if completed_count >= 5:
        badges.append({"name": "퀘스트 러너", "icon": "🏁", "tone": "success"})
    if completed_count >= 10:
        badges.append({"name": "베테랑", "icon": "⭐", "tone": "warning"})
    if streak >= 3:
        badges.append({"name": "연속 플레이", "icon": "🔥", "tone": "danger"})
    if any(t.get("note") for t in todos):
        badges.append({"name": "전략가", "icon": "🧠", "tone": "secondary"})

    quests = [
        {
            "title": "오늘 3개 완료",
            "current": today_completed,
            "target": 3,
            "reward": 100,
        },
        {
            "title": "오늘 1개 추가",
            "current": today_created,
            "target": 1,
            "reward": 30,
        },
    ]

    return {
        "xp": xp,
        "level": level,
        "level_current": level_current,
        "level_target": level_target,
        "level_progress": int((level_current / level_target) * 100) if level_target else 0,
        "streak": streak,
        "today_completed": today_completed,
        "today_created": today_created,
        "badges": badges,
        "quests": quests,
    }


def build_tree_summary(todos, game_state):
    tree = sync_tree_state(todos, game_state)
    total = len(todos)
    completed = sum(1 for t in todos if t["completed"])
    overdue = sum(
        1
        for t in todos
        if parse_due_datetime(t.get("due_date")) and not t["completed"] and parse_due_datetime(t.get("due_date")) < datetime.now()
    )
    return {
        "hp": tree["hp"],
        "hp_max": 100,
        "growth": tree["growth"],
        "growth_bonus": tree["growth_bonus"],
        "stage": tree["stage"],
        "stage_label": f"레벨 {tree['stage']}",
        "schedule_progress": tree["schedule_progress"],
        "health_label": tree["health_label"],
        "state_label": tree["state_label"],
        "dead": tree["dead"],
        "grave": tree["grave"],
        "death_reason": tree["death_reason"],
        "waterings_today": tree["waterings_today"],
        "free_water_used": tree["free_water_used"],
        "free_water_limit": 3,
        "overdue": overdue,
        "total": total,
        "completed": completed,
        "message": tree.get("message") or "",
        "last_event": tree.get("last_event") or "",
        "background_items": tree.get("background_items", []),
        "house": tree.get("house"),
        "outfit": tree.get("outfit"),
        "can_harvest": tree.get("can_harvest", False),
        "can_discard": tree.get("dead", False),
        "harvest_count": tree.get("harvest_count", 0),
        "harvested": tree.get("harvested", False),
        "free_water_date": tree.get("free_water_date"),
    }


def set_tree_dead(tree, reason, message):
    tree["hp"] = 0
    tree["dead"] = True
    tree["grave"] = True
    tree["death_reason"] = reason
    tree["message"] = message
    tree["last_event"] = message
    tree["health_label"] = "죽음"
    tree["state_label"] = "죽음"


def tree_warning_message(reason):
    if reason == "번개":
        return "번개가 나무를 태웠어요."
    if reason == "홍수":
        return "홍수에 나무가 쓸려갔어요."
    if reason == "일정 초과":
        return "일정 잘 지키라고!"
    return "일정 잘 지키라고!"


@app.route("/")
def index():
    return render_template("todo_web.html")


@app.route("/api/todos")
def api_todos():
    todos = normalize_todos(load_todos())
    game_state = load_game_state()
    tree = build_tree_summary(todos, game_state)
    save_game_state(game_state)
    def todo_sort_key(todo):
        return (
            -parse_created_datetime(todo.get("created_at")).timestamp(),
            -int(todo.get("id", 0)),
        )

    todos.sort(key=todo_sort_key)

    total = len(todos)
    completed = sum(1 for t in todos if t["completed"])
    pending = total - completed
    overdue = sum(
        1
        for t in todos
        if parse_due_datetime(t.get("due_date")) and not t["completed"] and parse_due_datetime(t.get("due_date")) < datetime.now()
    )
    gamification = build_gamification(todos)
    level, level_current, level_target = level_from_xp(game_state["xp"])
    gamification.update(
        {
            "xp": game_state["xp"],
            "coins": game_state["coins"],
            "level": level,
            "level_current": level_current,
            "level_target": level_target,
            "level_progress": int((level_current / level_target) * 100) if level_target else 0,
            "daily_mission": build_daily_mission(todos, game_state),
            "shop": build_shop(game_state),
            "boosts": game_state.get("boosts", {}),
            "tree": tree,
        }
    )

    return jsonify(
        {
            "stats": {
                "total": total,
                "completed": completed,
                "pending": pending,
                "progress": int((completed / total) * 100) if total else 0,
                "overdue": overdue,
            },
            "game": gamification,
            "todos": [
                {
                    **todo,
                    "priority_label": priority_label(todo["priority"]),
                    "due_meta": due_meta(todo),
                    "tree_meta": tree_meta(todo),
                }
                for todo in todos
            ],
        }
    )


@app.route("/api/todos", methods=["POST"])
def api_add_todo():
    data = request.get_json(force=True, silent=True) or request.form
    title = (data.get("title") or "").strip()
    priority = data.get("priority", "medium")
    due_date = (data.get("due_date") or "").strip()

    if not title:
        return jsonify({"ok": False, "error": "할일 내용을 입력하세요."}), 400

    if not due_date:
        return jsonify({"ok": False, "error": "마감일을 입력하세요."}), 400

    parsed_due = parse_due_datetime(due_date)
    if not parsed_due:
        return jsonify({"ok": False, "error": "마감일 형식이 올바르지 않습니다."}), 400

    todos = normalize_todos(load_todos())

    todos.append(
        {
            "id": next_id(todos),
            "title": title,
            "completed": False,
            "priority": priority,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "due_date": parsed_due.strftime("%Y-%m-%dT%H:%M"),
            "completed_at": None,
            "note": "",
            "tree_sold": False,
            "tree_decorations": [],
        }
    )
    save_todos(todos)
    return jsonify({"ok": True})


@app.route("/api/todos/<int:todo_id>/note", methods=["POST"])
def api_update_note(todo_id):
    data = request.get_json(force=True, silent=True) or request.form
    note = (data.get("note") or "").strip()

    todos = normalize_todos(load_todos())
    for todo in todos:
        if todo["id"] == todo_id:
            todo["note"] = note
            save_todos(todos)
            return jsonify({"ok": True})

    return jsonify({"ok": False, "error": "할일을 찾을 수 없습니다."}), 404


@app.route("/api/todos/<int:todo_id>/toggle", methods=["POST"])
def api_toggle_todo(todo_id):
    todos = normalize_todos(load_todos())
    game_state = load_game_state()
    for todo in todos:
        if todo["id"] == todo_id:
            was_completed = todo["completed"]
            todo["completed"] = not todo["completed"]
            todo["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M") if todo["completed"] else None
            save_todos(todos)
            level_before, _, _ = level_from_xp(game_state["xp"])
            xp_gain = 0
            coin_gain = 0
            if todo["completed"] and not was_completed:
                xp_gain, coin_gain = apply_completion_reward(todo, game_state)
                save_game_state(game_state)
            level_after, current_xp, target_xp = level_from_xp(game_state["xp"])
            return jsonify({
                "ok": True,
                "completed": todo["completed"],
                "xp_gain": xp_gain,
                "coin_gain": coin_gain,
                "leveled_up": level_after > level_before,
                "level": level_after,
                "xp": game_state["xp"],
                "xp_current": current_xp,
                "xp_target": target_xp,
                "coins": game_state["coins"],
            })
    return jsonify({"ok": False, "error": "할일을 찾을 수 없습니다."}), 404


@app.route("/api/todos/<int:todo_id>/sell-tree", methods=["POST"])
def api_sell_tree(todo_id):
    todos = normalize_todos(load_todos())
    game_state = load_game_state()
    for todo in todos:
        if todo["id"] == todo_id:
            if not todo.get("completed"):
                return jsonify({"ok": False, "error": "완료한 작업만 판매할 수 있습니다."}), 400
            if todo.get("tree_sold"):
                return jsonify({"ok": False, "error": "이미 판매한 나무입니다."}), 400
            reward = apply_tree_sale_reward(todo, game_state)
            todo["tree_sold"] = True
            save_todos(todos)
            save_game_state(game_state)
            return jsonify({"ok": True, "reward": reward, "coins": game_state["coins"]})
    return jsonify({"ok": False, "error": "할일을 찾을 수 없습니다."}), 404


@app.route("/api/todos/<int:todo_id>/decorate", methods=["POST"])
def api_decorate_tree(todo_id):
    data = request.get_json(force=True, silent=True) or request.form
    item_id = (data.get("item_id") or "tree_lantern").strip()
    todos = normalize_todos(load_todos())
    game_state = load_game_state()
    if item_id not in set(game_state.get("owned", [])):
        return jsonify({"ok": False, "error": "보유한 장식만 적용할 수 있습니다."}), 400

    for todo in todos:
        if todo["id"] == todo_id:
            decorations = todo.setdefault("tree_decorations", [])
            if item_id in decorations:
                return jsonify({"ok": False, "error": "이미 적용된 장식입니다."}), 400
            decorations.append(item_id)
            save_todos(todos)
            return jsonify({"ok": True, "decorations": decorations})
    return jsonify({"ok": False, "error": "할일을 찾을 수 없습니다."}), 404


@app.route("/api/tree/action", methods=["POST"])
def api_tree_action():
    data = request.get_json(force=True, silent=True) or request.form
    action = (data.get("action") or "").strip()
    todos = normalize_todos(load_todos())
    game_state = load_game_state()
    tree = sync_tree_state(todos, game_state)
    today = datetime.now().date().isoformat()

    if action == "water":
        if tree["dead"]:
            return jsonify({"ok": False, "error": "죽은 나무는 물을 줄 수 없습니다."}), 400
        free_available = tree.get("free_water_date") == today and tree.get("free_water_used", 0) < 3
        paid_cost = 10
        used_free = False
        if free_available:
            tree["free_water_used"] += 1
            used_free = True
        else:
            if game_state["coins"] < paid_cost:
                return jsonify({"ok": False, "error": "코인이 부족합니다."}), 400
            game_state["coins"] -= paid_cost
        tree["waterings_today"] += 1
        if tree["waterings_today"] <= 5:
            tree["hp"] = min(100, tree["hp"] + 6)
            tree["growth_bonus"] = min(100, tree["growth_bonus"] + 6)
            tree["message"] = "고마워요. 더 건강해졌어요."
            tree["last_event"] = "물주기 완료"
        else:
            tree["hp"] = max(0, tree["hp"] - 10)
            tree["message"] = "너무 많이 받았어요..."
            tree["last_event"] = "과도한 물주기"
            if tree["hp"] == 0:
                set_tree_dead(tree, "과도한 물주기", "물을 너무 많이 받아서 나무가 죽었어요.")
        tree["health_label"] = tree_health_label(tree["hp"])

    elif action == "medicine":
        if tree["dead"]:
            return jsonify({"ok": False, "error": "죽은 나무는 치료할 수 없습니다."}), 400
        cost = 25
        if game_state["coins"] < cost:
            return jsonify({"ok": False, "error": "코인이 부족합니다."}), 400
        game_state["coins"] -= cost
        tree["hp"] = min(100, tree["hp"] + 20)
        tree["message"] = "약 덕분에 많이 나아졌어요."
        tree["last_event"] = "약 사용"
        tree["health_label"] = tree_health_label(tree["hp"])

    elif action == "sap":
        if tree["dead"]:
            return jsonify({"ok": False, "error": "죽은 나무는 치료할 수 없습니다."}), 400
        cost = 20
        if game_state["coins"] < cost:
            return jsonify({"ok": False, "error": "코인이 부족합니다."}), 400
        game_state["coins"] -= cost
        tree["hp"] = min(100, tree["hp"] + 10)
        tree["message"] = "수액이 스며들었어요."
        tree["last_event"] = "수액 사용"
        tree["health_label"] = tree_health_label(tree["hp"])

    elif action == "harvest":
        if not tree.get("can_harvest"):
            return jsonify({"ok": False, "error": "아직 수확할 수 없습니다."}), 400
        reward = 50 + (tree.get("stage", 1) * 10) + (tree.get("schedule_progress", 0) // 10)
        game_state["coins"] += reward
        tree["harvest_count"] += 1
        tree["harvested"] = True
        tree["growth_bonus"] = 0
        tree["free_water_used"] = 0
        tree["waterings_today"] = 0
        tree["dead"] = False
        tree["grave"] = False
        tree["death_reason"] = None
        tree["hp"] = 100
        tree["message"] = "새싹을 다시 심었어요."
        tree["last_event"] = "수확 완료"
        tree["last_schedule_penalty_date"] = today
        tree["health_label"] = tree_health_label(tree["hp"])
        tree["state_label"] = tree["health_label"]
        save_game_state(game_state)
        return jsonify({"ok": True, "coins": game_state["coins"], "reward": reward, "tree": build_tree_summary(todos, game_state)})

    elif action == "lightning":
        if tree["dead"]:
            return jsonify({"ok": False, "error": "이미 죽은 나무입니다."}), 400
        hit = random.random() < 0.35
        if hit:
            set_tree_dead(tree, "번개", "번개에 나무가 탔어요.")
        else:
            tree["last_event"] = "번개가 빗나갔어요."
            tree["message"] = "위험했어요!"
        tree["health_label"] = tree_health_label(tree["hp"])

    elif action == "flood":
        if tree["dead"]:
            return jsonify({"ok": False, "error": "이미 죽은 나무입니다."}), 400
        hit = random.random() < 0.3
        if hit:
            tree["background_items"] = []
            set_tree_dead(tree, "홍수", "홍수에 모든 배경이 쓸려가고 나무가 죽었어요.")
        else:
            tree["last_event"] = "홍수가 지나갔어요."
            tree["message"] = "물살이 스쳤어요."
        tree["health_label"] = tree_health_label(tree["hp"])

    elif action == "discard":
        if not tree["dead"]:
            return jsonify({"ok": False, "error": "죽은 나무만 버릴 수 있습니다."}), 400
        tree.update(default_tree_state())
        tree["growth_bonus"] = -tree.get("schedule_progress", 0)
        tree["message"] = "새 새싹을 다시 키우기 시작했어요."
        tree["last_event"] = "나무를 버리고 새로 시작했어요."
        tree["health_label"] = tree_health_label(tree["hp"])
        tree["state_label"] = tree["health_label"]

    else:
        return jsonify({"ok": False, "error": "알 수 없는 행동입니다."}), 400

    tree["can_harvest"] = tree.get("growth", 0) >= 100 and not tree["dead"]
    save_game_state(game_state)
    return jsonify({"ok": True, "coins": game_state["coins"], "tree": build_tree_summary(todos, game_state)})


@app.route("/api/todos/<int:todo_id>", methods=["DELETE"])
def api_delete_todo(todo_id):
    todos = normalize_todos(load_todos())
    filtered = [todo for todo in todos if todo["id"] != todo_id]
    if len(filtered) == len(todos):
        return jsonify({"ok": False, "error": "할일을 찾을 수 없습니다."}), 404
    save_todos(filtered)
    return jsonify({"ok": True})


@app.route("/api/game/daily-claim", methods=["POST"])
def api_claim_daily():
    todos = normalize_todos(load_todos())
    game_state = load_game_state()
    mission = build_daily_mission(todos, game_state)
    if not mission["can_claim"]:
        return jsonify({"ok": False, "error": "퀘스트를 아직 완료하지 못했습니다."}), 400

    today = datetime.now().date().isoformat()
    game_state["coins"] += mission["reward"]
    game_state["daily_claimed"] = today
    save_game_state(game_state)
    return jsonify({"ok": True, "reward": mission["reward"], "coins": game_state["coins"]})


@app.route("/api/shop/buy", methods=["POST"])
def api_buy_shop():
    data = request.get_json(force=True, silent=True) or request.form
    item_id = data.get("item_id")
    items = {item["id"]: item for item in shop_items()}
    if item_id not in items:
        return jsonify({"ok": False, "error": "상품을 찾을 수 없습니다."}), 404

    game_state = load_game_state()
    item = items[item_id]
    if game_state["coins"] < item["price"]:
        return jsonify({"ok": False, "error": "코인이 부족합니다."}), 400

    game_state["coins"] -= item["price"]
    if item["kind"] == "cosmetic":
        if item_id not in game_state["owned"]:
            game_state["owned"].append(item_id)
    elif item_id == "xp_boost":
        game_state["boosts"]["xp_uses"] += 5
    elif item_id == "coin_crate":
        game_state["boosts"]["coin_uses"] += 5

    save_game_state(game_state)
    return jsonify({"ok": True, "coins": game_state["coins"]})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
