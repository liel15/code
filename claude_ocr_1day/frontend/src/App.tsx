import React, { useEffect, useMemo, useState } from "react";
import Header, { DashboardTab } from "./components/Header";

type ViewProps = {
  activeTab: DashboardTab;
};

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<DashboardTab>(() => resolveTab(window.location.hash, window.location.pathname));

  useEffect(() => {
    const onHashChange = () => setActiveTab(resolveTab(window.location.hash, window.location.pathname));
    window.addEventListener("hashchange", onHashChange);
    return () => window.removeEventListener("hashchange", onHashChange);
  }, []);

  const navigate = (tab: DashboardTab) => {
    window.location.hash = tab;
  };

  const theme = useMemo(() => {
    switch (activeTab) {
      case "schedule":
        return {
          bg: "radial-gradient(circle at 15% 12%, rgba(83,226,155,.18), transparent 18%), radial-gradient(circle at 85% 18%, rgba(133,216,255,.10), transparent 16%), linear-gradient(180deg, #07130f 0%, #0c1f16 100%)",
          title: "일정",
          subtitle: "시간보다 흐름 중심으로 정리",
        };
      case "growth":
        return {
          bg: "radial-gradient(circle at 20% 10%, rgba(255,203,107,.18), transparent 18%), radial-gradient(circle at 70% 20%, rgba(83,226,155,.12), transparent 20%), linear-gradient(180deg, #0d140f 0%, #08110c 100%)",
          title: "성장",
          subtitle: "완료할수록 나무가 더 풍성해짐",
        };
      case "insight":
        return {
          bg: "radial-gradient(circle at 15% 12%, rgba(133,216,255,.18), transparent 18%), radial-gradient(circle at 80% 14%, rgba(255,125,143,.12), transparent 16%), linear-gradient(180deg, #0b1118 0%, #081016 100%)",
          title: "인사이트",
          subtitle: "패턴을 읽고 다음 행동을 제안",
        };
      default:
        return {
          bg: "radial-gradient(circle at 15% 12%, rgba(83,226,155,.20), transparent 20%), radial-gradient(circle at 80% 10%, rgba(133,216,255,.16), transparent 18%), linear-gradient(180deg, #05110c 0%, #07130f 100%)",
          title: "오늘",
          subtitle: "자유로운 분위기와 리듬",
        };
    }
  }, [activeTab]);

  return (
    <div style={{ minHeight: "100vh", color: "#effaf2", background: theme.bg }}>
      <style>{`
        @keyframes floaty {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-10px); }
        }
      `}</style>
      <div style={styles.noise} />
      <main style={styles.wrap}>
        <Header activeTab={activeTab} onTabChange={navigate} />
        <div style={styles.themeBanner}>
          <strong style={styles.themeBannerStrong}>{theme.title}</strong>
          <span>{theme.subtitle}</span>
        </div>
        <View activeTab={activeTab} />
      </main>
    </div>
  );
};

const resolveTab = (hash: string, pathname: string): DashboardTab => {
  const hashTab = hash.replace("#", "") as DashboardTab;
  if (hashTab === "today" || hashTab === "schedule" || hashTab === "growth" || hashTab === "insight") {
    return hashTab;
  }
  if (pathname.endsWith("/schedule")) return "schedule";
  if (pathname.endsWith("/growth")) return "growth";
  if (pathname.endsWith("/insight")) return "insight";
  return "today";
};

const View: React.FC<ViewProps> = ({ activeTab }) => {
  if (activeTab === "schedule") return <ScheduleView />;
  if (activeTab === "growth") return <GrowthView />;
  if (activeTab === "insight") return <InsightView />;
  return <TodayView />;
};

const TodayView: React.FC = () => (
  <section style={styles.hero}>
    <div style={{ ...styles.panel, ...styles.heroMain }}>
      <div style={styles.eyebrow}>🌱 오늘 · 자유로운 분위기와 리듬</div>
      <h1 style={styles.h1}>할 일을 심고, 나무로 자라나는 일정관리</h1>
      <p style={styles.lead}>
        딱딱한 체크리스트 대신, 하루의 태스크가 잎과 가지가 되어 성장하는 화면입니다.
        계획은 가볍게 정리하고, 진행은 시각적으로 느껴지도록 구성했습니다.
      </p>
      <div style={styles.actions}>
        <button style={styles.primaryButton}>새 일정 심기</button>
        <button style={styles.ghostButton}>빠른 메모</button>
      </div>
      <div style={styles.stats}>
        <Stat label="오늘의 일정" value="8개" hint="가벼운 리듬으로 배치" />
        <Stat label="성장 단계" value="78%" hint="잎이 무성해지는 중" />
        <Stat label="집중 시간" value="4h 20m" hint="깊은 작업 블록 유지" />
      </div>
    </div>

    <div style={{ ...styles.panel, ...styles.treeShell }}>
      <div style={styles.panelHead}>
        <div>
          <h2 style={styles.h2}>오늘의 나무</h2>
          <p style={styles.sub}>완료된 일정이 가지를 키웁니다</p>
        </div>
        <span style={styles.pill}>활력 +12</span>
      </div>
      <TreeStage />
      <div style={styles.badgeRow}>
        <span style={styles.badge}>물주기: 오전 1회</span>
        <span style={styles.badge}>햇빛: 집중 블록</span>
        <span style={styles.badge}>비료: 완료 체크</span>
      </div>
    </div>
  </section>
);

const ScheduleView: React.FC = () => (
  <section style={styles.grid}>
    <article style={styles.card}>
      <div style={styles.panelHead}>
        <div>
          <h2 style={styles.h2}>오늘 심을 일정</h2>
          <p style={styles.sub}>시간 대신 흐름 중심으로 정리</p>
        </div>
        <span style={styles.pill}>3개 우선</span>
      </div>
      <div style={styles.taskList}>
        <TaskItem title="프로젝트 문구 다듬기" meta="10:00 · 짧은 집중 세션 · 톤 정리와 카피 수정" pill="새싹" />
        <TaskItem title="회의 노트 정리" meta="13:30 · 중간 난이도 · 핵심 액션 항목 분리" pill="잎" />
        <TaskItem title="저녁 운동 루틴" meta="18:20 · 회복 일정 · 휴식과 리듬 관리" pill="꽃" />
      </div>
    </article>
    <aside style={styles.card}>
      <div style={styles.panelHead}>
        <div>
          <h2 style={styles.h2}>배치 감각</h2>
          <p style={styles.sub}>하루의 리듬을 시각화</p>
        </div>
      </div>
      <MiniGrid />
    </aside>
  </section>
);

const GrowthView: React.FC = () => (
  <section style={styles.grid}>
    <div style={{ ...styles.panel, ...styles.treeShell }}>
      <div style={styles.panelHead}>
        <div>
          <h2 style={styles.h2}>성장하는 나무</h2>
          <p style={styles.sub}>완료할수록 형태가 풍성해짐</p>
        </div>
        <span style={styles.pill}>성장 +78</span>
      </div>
      <TreeStage />
      <div style={styles.badgeRow}>
        <span style={styles.badge}>새 잎 12장</span>
        <span style={styles.badge}>가지 4개 확장</span>
        <span style={styles.badge}>꽃 2개 개화</span>
      </div>
    </div>
    <article style={styles.card}>
      <div style={styles.panelHead}>
        <div>
          <h2 style={styles.h2}>성장 지표</h2>
          <p style={styles.sub}>작업이 나무에 남기는 흔적</p>
        </div>
      </div>
      <Meter label="집중 루트" value={82} />
      <Meter label="완료 가지" value={64} />
      <Meter label="회복 햇빛" value={91} />
      <div style={styles.notes}>
        <Note title="자라나는 방식" text="완료된 일정이 잎과 가지로 시각화되어, 오늘의 성취를 감각적으로 느낄 수 있습니다." />
        <Note title="리듬의 보상" text="작은 완료도 화면의 밀도와 색감에 반영되어, 다음 행동으로 자연스럽게 이어집니다." />
      </div>
    </article>
  </section>
);

const InsightView: React.FC = () => (
  <section style={styles.grid}>
    <article style={styles.card}>
      <div style={styles.panelHead}>
        <div>
          <h2 style={styles.h2}>인사이트</h2>
          <p style={styles.sub}>일정의 패턴을 읽는 공간</p>
        </div>
      </div>
      <Meter label="집중 루트" value={82} />
      <Meter label="완료 가지" value={64} />
      <Meter label="회복 햇빛" value={91} />
    </article>
    <aside style={styles.card}>
      <div style={styles.panelHead}>
        <div>
          <h2 style={styles.h2}>오늘의 메모</h2>
          <p style={styles.sub}>가볍지만 의미 있는 피드백</p>
        </div>
      </div>
      <div style={styles.notes}>
        <Note title="자유로운 배치" text="시간표보다 분위기를 먼저 읽는 레이아웃으로, 오늘의 우선순위를 시각적으로 느끼게 합니다." />
        <Note title="성장 피드백" text="완료된 일정은 단순히 체크되지 않고, 나무의 형태와 색감 변화로 즉시 피드백됩니다." />
        <Note title="다음 추천" text="집중 루트가 높은 시간대에 가장 무거운 작업을 배치하면 더 자연스럽게 자라납니다." />
      </div>
    </aside>
  </section>
);

const TreeStage: React.FC = () => (
  <div style={styles.treeStage}>
    <div style={styles.sun} />
    <div style={styles.treeWrap}>
      <div style={styles.crownWrap}>
        <div style={{ ...styles.orb, ...styles.orbOne }} />
        <div style={{ ...styles.orb, ...styles.orbTwo }} />
        <div style={{ ...styles.orb, ...styles.orbThree }} />
        <div style={{ ...styles.orb, ...styles.orbFour }} />
      </div>
      <div style={styles.trunk} />
      <div style={styles.soil} />
      <div style={styles.hill} />
    </div>
  </div>
);

const Stat: React.FC<{ label: string; value: string; hint: string }> = ({ label, value, hint }) => (
  <div style={styles.stat}>
    <div style={styles.statLabel}>{label}</div>
    <div style={styles.statValue}>{value}</div>
    <div style={styles.statHint}>{hint}</div>
  </div>
);

const TaskItem: React.FC<{ title: string; meta: string; pill: string }> = ({ title, meta, pill }) => (
  <div style={styles.task}>
    <div style={styles.dot} />
    <div>
      <h3 style={styles.taskTitle}>{title}</h3>
      <div style={styles.taskMeta}>{meta}</div>
    </div>
    <div style={styles.pill}>{pill}</div>
  </div>
);

const MiniGrid: React.FC = () => (
  <div style={styles.miniGrid}>
    <MiniCard title="오전" text="가벼운 편집과 준비 작업을 중심으로 잔가지처럼 펼칩니다." />
    <MiniCard title="오후" text="핵심 업무를 묶어 중간 굵기의 줄기로 이어줍니다." />
    <MiniCard title="저녁" text="회복과 루틴 정리로 잔잔한 하이라이트를 남깁니다." />
    <MiniCard title="유연성" text="정해진 칸보다 흐름에 따라 자유롭게 이동할 수 있습니다." />
  </div>
);

const MiniCard: React.FC<{ title: string; text: string }> = ({ title, text }) => (
  <div style={styles.miniCard}>
    <strong style={styles.miniTitle}>{title}</strong>
    <span style={styles.miniText}>{text}</span>
  </div>
);

const Meter: React.FC<{ label: string; value: number }> = ({ label, value }) => (
  <div style={styles.meter}>
    <div style={styles.meterRow}>
      <span>{label}</span>
      <strong>{value}%</strong>
    </div>
    <div style={styles.bar}>
      <span style={{ ...styles.barFill, width: `${value}%` }} />
    </div>
  </div>
);

const Note: React.FC<{ title: string; text: string }> = ({ title, text }) => (
  <div style={styles.note}>
    <strong style={styles.noteTitle}>{title}</strong>
    <span style={styles.noteText}>{text}</span>
  </div>
);

const styles: Record<string, React.CSSProperties> = {
  noise: {
    position: "fixed",
    inset: 0,
    pointerEvents: "none",
    opacity: 0.12,
    backgroundImage:
      "linear-gradient(rgba(255,255,255,.02) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.02) 1px, transparent 1px)",
    backgroundSize: "42px 42px",
    maskImage: "linear-gradient(180deg, rgba(0,0,0,.9), rgba(0,0,0,.3))",
  },
  wrap: {
    width: "min(1220px, calc(100% - 28px))",
    margin: "0 auto",
    padding: "24px 0 44px",
    position: "relative",
    zIndex: 1,
  },
  themeBanner: {
    display: "flex",
    alignItems: "center",
    gap: 10,
    marginTop: 14,
    padding: "10px 14px",
    borderRadius: 16,
    border: "1px solid rgba(255,255,255,.08)",
    background: "rgba(255,255,255,.04)",
    color: "#a7c0b1",
  },
  themeBannerStrong: { color: "#effaf2" },
  hero: { display: "grid", gridTemplateColumns: "1.15fr .85fr", gap: 18, marginTop: 18 },
  grid: { display: "grid", gridTemplateColumns: "1.05fr .95fr", gap: 18, marginTop: 18 },
  panel: {
    border: "1px solid rgba(255,255,255,.08)",
    borderRadius: 34,
    background: "linear-gradient(180deg, rgba(255,255,255,.05), rgba(255,255,255,.025))",
    backdropFilter: "blur(18px)",
    boxShadow: "0 24px 70px rgba(0,0,0,.34)",
  },
  heroMain: {
    padding: 34,
    overflow: "hidden",
    position: "relative",
    background:
      "radial-gradient(circle at 85% 12%, rgba(255,203,107,.16), transparent 22%), radial-gradient(circle at 20% 0%, rgba(83,226,155,.14), transparent 20%), linear-gradient(145deg, rgba(15, 31, 21, .96), rgba(8, 18, 12, .96))",
  },
  eyebrow: {
    display: "inline-flex",
    alignItems: "center",
    gap: 8,
    padding: "9px 14px",
    marginBottom: 16,
    borderRadius: 999,
    border: "1px solid rgba(83,226,155,.22)",
    background: "rgba(83,226,155,.08)",
    color: "#b8ffd9",
    fontSize: "0.92rem",
  },
  h1: { margin: 0, maxWidth: "11ch", fontSize: "clamp(2.5rem, 4.6vw, 5rem)", lineHeight: 0.95, letterSpacing: "-0.07em" },
  lead: { maxWidth: "54ch", margin: "18px 0 26px", color: "#a7c0b1", lineHeight: 1.75, fontSize: "1.02rem" },
  actions: { display: "flex", flexWrap: "wrap", gap: 12, marginBottom: 22 },
  primaryButton: {
    minHeight: 48,
    padding: "0 18px",
    borderRadius: 18,
    border: "1px solid transparent",
    fontWeight: 800,
    color: "#072014",
    background: "linear-gradient(135deg, #53e29b, #90f0c0)",
    boxShadow: "0 18px 40px rgba(83,226,155,.18)",
    cursor: "pointer",
  },
  ghostButton: {
    minHeight: 48,
    padding: "0 18px",
    borderRadius: 18,
    border: "1px solid rgba(255,255,255,.1)",
    fontWeight: 800,
    color: "#effaf2",
    background: "rgba(255,255,255,.045)",
    cursor: "pointer",
  },
  stats: { display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 14, marginTop: 10 },
  stat: { padding: 16, borderRadius: 20, border: "1px solid rgba(255,255,255,.08)", background: "rgba(255,255,255,.04)" },
  statLabel: { color: "#a7c0b1", fontSize: "0.88rem", marginBottom: 8 },
  statValue: { fontSize: "1.85rem", fontWeight: 900, letterSpacing: "-0.04em" },
  statHint: { marginTop: 6, color: "#a7c0b1", fontSize: "0.86rem" },
  treeShell: { display: "grid", gridTemplateRows: "auto 1fr auto", minHeight: "100%", padding: 24, position: "relative", overflow: "hidden", background: "linear-gradient(180deg, rgba(14,28,20,.95), rgba(8,16,12,.98))" },
  panelHead: { display: "flex", alignItems: "end", justifyContent: "space-between", gap: 12, marginBottom: 16 },
  h2: { margin: 0, fontSize: "1.2rem", letterSpacing: "-0.04em" },
  sub: { margin: 0, color: "#a7c0b1", fontSize: "0.9rem" },
  pill: { padding: "8px 12px", borderRadius: 999, fontSize: "0.82rem", fontWeight: 800, background: "rgba(83,226,155,.1)", color: "#a8ffd0", border: "1px solid rgba(83,226,155,.16)" },
  treeStage: { position: "relative", minHeight: 380, borderRadius: 30, border: "1px solid rgba(255,255,255,.08)", background: "radial-gradient(circle at 50% 0%, rgba(133,216,255,.14), transparent 22%), radial-gradient(circle at 50% 100%, rgba(83,226,155,.10), transparent 22%), linear-gradient(180deg, rgba(11,23,16,.92), rgba(8,16,12,.92))", overflow: "hidden" },
  sun: { position: "absolute", right: 22, top: 22, width: 86, height: 86, borderRadius: "50%", background: "radial-gradient(circle at 35% 35%, #fff7d4, #ffcb6b)", boxShadow: "0 0 50px rgba(255,203,107,.18)", opacity: 0.95, transform: "translateZ(0)" },
  treeWrap: { position: "absolute", inset: 0, display: "grid", placeItems: "center", zIndex: 1 },
  crownWrap: { position: "absolute", top: 64, width: 320, height: 250 },
  orb: { position: "absolute", borderRadius: "50%", background: "radial-gradient(circle at 35% 35%, #d9ffe9, #53e29b)", boxShadow: "0 18px 40px rgba(83,226,155,.14), inset 0 -10px 18px rgba(10, 40, 22, .16)" },
  orbOne: { width: 126, height: 126, left: 92, top: 52, animation: "floaty 7s ease-in-out infinite" },
  orbTwo: { width: 160, height: 160, left: 0, top: 56, animation: "floaty 8s ease-in-out infinite .4s" },
  orbThree: { width: 152, height: 152, right: 0, top: 42, animation: "floaty 7.5s ease-in-out infinite .8s" },
  orbFour: { width: 110, height: 110, left: 108, top: 0, background: "radial-gradient(circle at 35% 35%, #f4fff8, #90f0c0)", animation: "floaty 6.8s ease-in-out infinite .2s" },
  trunk: { width: 56, height: 176, borderRadius: "30px 30px 18px 18px", background: "linear-gradient(180deg, #8c6342, #5d402a 75%)", position: "relative", boxShadow: "inset 0 -10px 0 rgba(0,0,0,.08)", transform: "translateY(58px)" },
  soil: { position: "absolute", left: "50%", bottom: 10, transform: "translateX(-50%)", width: 240, height: 90, borderRadius: "50%", background: "radial-gradient(circle at 50% 40%, rgba(255,255,255,.08), rgba(122,90,58,.55) 55%, rgba(52,34,18,.8) 100%)" },
  hill: { position: "absolute", left: "-8%", right: "-8%", bottom: -2, height: "34%", background: "linear-gradient(180deg, rgba(37,72,45,.18), rgba(58,100,62,.55))", clipPath: "ellipse(54% 44% at 50% 100%)" },
  badgeRow: { display: "flex", flexWrap: "wrap", gap: 10, marginTop: 16 },
  badge: { padding: "8px 12px", borderRadius: 999, border: "1px solid rgba(255,255,255,.08)", background: "rgba(255,255,255,.04)", color: "#a7c0b1", fontSize: "0.86rem" },
  card: { padding: 22, borderRadius: 28, border: "1px solid rgba(255,255,255,.08)", background: "rgba(255,255,255,.04)", backdropFilter: "blur(18px)", boxShadow: "0 24px 70px rgba(0,0,0,.34)" },
  taskList: { display: "grid", gap: 12 },
  task: { display: "grid", gridTemplateColumns: "auto 1fr auto", gap: 14, alignItems: "center", padding: 16, borderRadius: 20, border: "1px solid rgba(255,255,255,.08)", background: "linear-gradient(180deg, rgba(255,255,255,.05), rgba(255,255,255,.03))" },
  dot: { width: 16, height: 16, borderRadius: "50%", background: "linear-gradient(135deg, #53e29b, #90f0c0)", boxShadow: "0 0 0 6px rgba(83,226,155,.12)" },
  taskTitle: { margin: "0 0 4px", fontSize: "1rem" },
  taskMeta: { color: "#a7c0b1", fontSize: "0.88rem", lineHeight: 1.5 },
  miniGrid: { display: "grid", gridTemplateColumns: "repeat(2, minmax(0, 1fr))", gap: 12 },
  miniCard: { padding: 16, borderRadius: 20, border: "1px solid rgba(255,255,255,.08)", background: "rgba(255,255,255,.04)" },
  miniTitle: { display: "block", marginBottom: 8, fontSize: "1.05rem" },
  miniText: { color: "#a7c0b1", fontSize: "0.9rem", lineHeight: 1.55 },
  meter: { padding: "14px 16px", borderRadius: 18, background: "rgba(255,255,255,.04)", border: "1px solid rgba(255,255,255,.08)", marginBottom: 12 },
  meterRow: { display: "flex", justifyContent: "space-between", gap: 12, marginBottom: 10, color: "#a7c0b1", fontSize: "0.9rem" },
  bar: { height: 10, borderRadius: 999, background: "rgba(255,255,255,.06)", overflow: "hidden" },
  barFill: { display: "block", height: "100%", borderRadius: 999, background: "linear-gradient(90deg, #53e29b, #85d8ff)" },
  notes: { display: "grid", gap: 12, marginTop: 18 },
  note: { padding: 16, borderRadius: 20, border: "1px solid rgba(255,255,255,.08)", background: "rgba(255,255,255,.04)" },
  noteTitle: { display: "block", marginBottom: 6 },
  noteText: { color: "#a7c0b1", fontSize: "0.9rem", lineHeight: 1.55 },
};

export default App;
