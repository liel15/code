import json
import os
import tempfile
import unittest
from unittest.mock import patch

import todo_web


class TodoWebTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        todo_web.DATA_FILE = os.path.join(self.tmpdir.name, "todos.json")
        todo_web.GAME_FILE = os.path.join(self.tmpdir.name, "game_state.json")
        todo_web.app.config["TESTING"] = True
        self.client = todo_web.app.test_client()
        todo_web.save_todos([])
        todo_web.save_game_state(
            {
                "xp": 0,
                "coins": 200,
                "owned": [],
                "boosts": {"xp_uses": 0, "coin_uses": 0},
                "daily_claimed": None,
                "tree": todo_web.default_tree_state(),
            }
        )

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_add_todo_requires_due_date(self):
        res = self.client.post("/api/todos", json={"title": "테스트", "priority": "medium"})
        self.assertEqual(res.status_code, 400)

    def test_add_todo_normalizes_due_date(self):
        res = self.client.post(
            "/api/todos",
            json={"title": "테스트", "priority": "high", "due_date": "2026-05-03T12:30"},
        )
        self.assertEqual(res.status_code, 200)
        todos = todo_web.load_todos()
        self.assertEqual(todos[0]["due_date"], "2026-05-03T12:30")

    def test_todos_api_includes_due_and_tree_meta(self):
        todo_web.save_todos(
            [
                {
                    "id": 1,
                    "title": "늦은 일정",
                    "completed": False,
                    "priority": "medium",
                    "created_at": "2026-05-02 10:00",
                    "due_date": "2026-05-02T09:00",
                    "completed_at": None,
                    "note": "",
                    "tree_sold": False,
                    "tree_decorations": [],
                }
            ]
        )
        res = self.client.get("/api/todos")
        self.assertEqual(res.status_code, 200)
        payload = res.get_json()
        todo = payload["todos"][0]
        self.assertEqual(todo["due_meta"]["kind"], "overdue")
        self.assertEqual(todo["tree_meta"]["label"], "시든 나무")

    def test_tree_sale_is_single_use(self):
        todo_web.save_todos(
            [
                {
                    "id": 1,
                    "title": "완료 일정",
                    "completed": True,
                    "priority": "high",
                    "created_at": "2026-05-02 10:00",
                    "due_date": "2026-05-03T12:30",
                    "completed_at": "2026-05-02 11:00",
                    "note": "",
                    "tree_sold": False,
                    "tree_decorations": [],
                }
            ]
        )
        first = self.client.post("/api/todos/1/sell-tree")
        self.assertEqual(first.status_code, 200)
        second = self.client.post("/api/todos/1/sell-tree")
        self.assertEqual(second.status_code, 400)

    def test_tree_decoration_requires_owned_item(self):
        todo_web.save_game_state(
            {
                "xp": 0,
                "coins": 200,
                "owned": ["tree_lantern"],
                "boosts": {"xp_uses": 0, "coin_uses": 0},
                "daily_claimed": None,
            }
        )
        todo_web.save_todos(
            [
                {
                    "id": 1,
                    "title": "장식 일정",
                    "completed": False,
                    "priority": "medium",
                    "created_at": "2026-05-02 10:00",
                    "due_date": "2026-05-05T12:30",
                    "completed_at": None,
                    "note": "",
                    "tree_sold": False,
                    "tree_decorations": [],
                }
            ]
        )
        res = self.client.post("/api/todos/1/decorate", json={"item_id": "tree_lantern"})
        self.assertEqual(res.status_code, 200)
        todos = todo_web.load_todos()
        self.assertEqual(todos[0]["tree_decorations"], ["tree_lantern"])

    def test_tree_api_applies_schedule_penalty_and_reports_tree(self):
        todo_web.save_todos(
            [
                {
                    "id": 1,
                    "title": "지연 일정",
                    "completed": False,
                    "priority": "medium",
                    "created_at": "2026-05-01 10:00",
                    "due_date": "2026-05-01T09:00",
                    "completed_at": None,
                    "note": "",
                    "tree_sold": False,
                    "tree_decorations": [],
                }
            ]
        )
        res = self.client.get("/api/todos")
        self.assertEqual(res.status_code, 200)
        payload = res.get_json()
        self.assertEqual(payload["game"]["tree"]["hp"], 88)
        self.assertEqual(payload["game"]["tree"]["state_label"], "건강함")

    def test_tree_actions_support_water_heal_harvest_and_disasters(self):
        todo_web.save_todos(
            [
                {
                    "id": 1,
                    "title": "완료 일정",
                    "completed": True,
                    "priority": "high",
                    "created_at": "2026-05-02 10:00",
                    "due_date": "2026-05-03T12:30",
                    "completed_at": "2026-05-02 11:00",
                    "note": "",
                    "tree_sold": False,
                    "tree_decorations": [],
                }
            ]
        )
        todo_web.save_game_state(
            {
                "xp": 0,
                "coins": 200,
                "owned": [],
                "boosts": {"xp_uses": 0, "coin_uses": 0},
                "daily_claimed": None,
                "tree": {
                    **todo_web.default_tree_state(),
                    "growth_bonus": 100,
                    "hp": 50,
                    "free_water_used": 0,
                    "waterings_today": 0,
                },
            }
        )

        water = self.client.post("/api/tree/action", json={"action": "water"})
        self.assertEqual(water.status_code, 200)
        water_payload = water.get_json()
        self.assertEqual(water_payload["tree"]["waterings_today"], 1)
        self.assertGreaterEqual(water_payload["tree"]["hp"], 50)

        medicine = self.client.post("/api/tree/action", json={"action": "medicine"})
        self.assertEqual(medicine.status_code, 200)
        self.assertGreater(medicine.get_json()["tree"]["hp"], water_payload["tree"]["hp"])

        harvest = self.client.post("/api/tree/action", json={"action": "harvest"})
        self.assertEqual(harvest.status_code, 200)
        self.assertGreater(harvest.get_json()["reward"], 0)

        with patch("todo_web.random.random", return_value=0.0):
            lightning = self.client.post("/api/tree/action", json={"action": "lightning"})
        self.assertEqual(lightning.status_code, 200)
        self.assertTrue(lightning.get_json()["tree"]["dead"])

        dead_water = self.client.post("/api/tree/action", json={"action": "water"})
        self.assertEqual(dead_water.status_code, 400)
        dead_medicine = self.client.post("/api/tree/action", json={"action": "medicine"})
        self.assertEqual(dead_medicine.status_code, 400)

        discard = self.client.post("/api/tree/action", json={"action": "discard"})
        self.assertEqual(discard.status_code, 200)
        discard_payload = discard.get_json()
        self.assertFalse(discard_payload["tree"]["dead"])
        self.assertFalse(discard_payload["tree"]["grave"])
        self.assertEqual(discard_payload["tree"]["stage"], 1)
        self.assertEqual(discard_payload["tree"]["growth"], 0)

        todo_web.save_game_state(
            {
                "xp": 0,
                "coins": 200,
                "owned": [],
                "boosts": {"xp_uses": 0, "coin_uses": 0},
                "daily_claimed": None,
                "tree": todo_web.default_tree_state(),
            }
        )
        with patch("todo_web.random.random", return_value=0.0):
            flood = self.client.post("/api/tree/action", json={"action": "flood"})
        self.assertEqual(flood.status_code, 200)
        flood_payload = flood.get_json()
        self.assertTrue(flood_payload["tree"]["dead"])
        self.assertEqual(flood_payload["tree"]["background_items"], [])


if __name__ == "__main__":
    unittest.main()
