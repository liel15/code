import React from "react";

export type DashboardTab = "today" | "schedule" | "growth" | "insight";

type HeaderProps = {
  activeTab: DashboardTab;
  onTabChange: (tab: DashboardTab) => void;
};

const tabs: Array<{ key: DashboardTab; label: string }> = [
  { key: "today", label: "오늘" },
  { key: "schedule", label: "일정" },
  { key: "growth", label: "성장" },
  { key: "insight", label: "인사이트" },
];

const Header: React.FC<HeaderProps> = ({ activeTab, onTabChange }) => {
  return (
    <header style={styles.header}>
      <div style={styles.brandWrap}>
        <div style={styles.brandMark}>🌿</div>
        <div>
          <div style={styles.brandTitle}>일정관리 나무 키우기</div>
          <div style={styles.brandSub}>자유롭고 감성적인 성장형 일정 보드</div>
        </div>
      </div>

      <nav style={styles.nav}>
        {tabs.map((tab) => (
          <button
            key={tab.key}
            type="button"
            onClick={() => onTabChange(tab.key)}
            style={{
              ...styles.tab,
              ...(activeTab === tab.key ? styles.tabActive : null),
            }}
          >
            {tab.label}
          </button>
        ))}
      </nav>
    </header>
  );
};

const styles: Record<string, React.CSSProperties> = {
  header: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    gap: 16,
    padding: "14px 16px",
    border: "1px solid rgba(255,255,255,0.08)",
    borderRadius: 999,
    background: "rgba(9, 20, 15, 0.66)",
    backdropFilter: "blur(18px)",
    boxShadow: "0 24px 70px rgba(0,0,0,0.34)",
    color: "#effaf2",
  },
  brandWrap: {
    display: "flex",
    alignItems: "center",
    gap: 12,
    fontWeight: 800,
    letterSpacing: "-0.04em",
  },
  brandMark: {
    width: 42,
    height: 42,
    borderRadius: 14,
    display: "grid",
    placeItems: "center",
    color: "#072014",
    background: "linear-gradient(135deg, #53e29b, #90f0c0)",
    boxShadow: "0 16px 30px rgba(83,226,155,0.18)",
  },
  brandTitle: {
    fontSize: "1rem",
  },
  brandSub: {
    color: "#a7c0b1",
    fontSize: "0.86rem",
    marginTop: 3,
    fontWeight: 500,
  },
  nav: {
    display: "flex",
    gap: 8,
    flexWrap: "wrap",
  },
  tab: {
    padding: "10px 14px",
    borderRadius: 999,
    border: "1px solid transparent",
    background: "transparent",
    color: "#a7c0b1",
    cursor: "pointer",
    font: "inherit",
  },
  tabActive: {
    color: "#effaf2",
    background: "rgba(83,226,155,0.08)",
    borderColor: "rgba(83,226,155,0.22)",
  },
};

export default Header;
