import {
  AppBar,
  Box,
  Drawer,
  IconButton,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Tooltip,
  Typography,
} from "@mui/material";
import AssessmentIcon from "@mui/icons-material/Assessment";
import AccessibilityNewIcon from "@mui/icons-material/AccessibilityNew";
import HomeIcon from "@mui/icons-material/Home";
import HubIcon from "@mui/icons-material/Hub";
import LogoutIcon from "@mui/icons-material/Logout";
import RecordVoiceOverIcon from "@mui/icons-material/RecordVoiceOver";
import TimelineIcon from "@mui/icons-material/Timeline";
import VerifiedIcon from "@mui/icons-material/Verified";
import Brightness4Icon from "@mui/icons-material/Brightness4";
import TextIncreaseIcon from "@mui/icons-material/TextIncrease";
import TextDecreaseIcon from "@mui/icons-material/TextDecrease";
import PaletteIcon from "@mui/icons-material/Palette";
import { useEffect } from "react";
import { Outlet, useLocation, useNavigate } from "react-router-dom";
import { useAccessibility } from "../context/AccessibilityContext";
import { useAuth } from "../context/AuthContext";

const drawerWidth = 240;

const NAV = [
  { label: "Home", path: "/", icon: <HomeIcon /> },
  { label: "Climate Analytics", path: "/analytics", icon: <AssessmentIcon /> },
  { label: "Accessibility", path: "/accessibility", icon: <AccessibilityNewIcon /> },
  { label: "Data Quality", path: "/data-quality", icon: <VerifiedIcon /> },
  { label: "Interoperability", path: "/interoperability", icon: <HubIcon /> },
  { label: "Forecast", path: "/forecast", icon: <TimelineIcon /> },
];

export default function Layout() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();
  const {
    cycleTheme,
    themeMode,
    increaseFont,
    decreaseFont,
    colorBlind,
    setColorBlind,
    ttsEnabled,
    setTtsEnabled,
    speakIfEnabled,
  } = useAccessibility();

  // Keyboard shortcuts: Alt+1..6 navigate, Alt+T theme, Alt+= / Alt+- font scale
  useEffect(() => {
    const handler = (e) => {
      if (!e.altKey) return;
      const idx = parseInt(e.key, 10);
      if (idx >= 1 && idx <= NAV.length) {
        navigate(NAV[idx - 1].path);
        e.preventDefault();
      } else if (e.key.toLowerCase() === "t") {
        cycleTheme();
        e.preventDefault();
      } else if (e.key === "=" || e.key === "+") {
        increaseFont();
        e.preventDefault();
      } else if (e.key === "-") {
        decreaseFont();
        e.preventDefault();
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [navigate, cycleTheme, increaseFont, decreaseFont]);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <Box sx={{ display: "flex" }}>
      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>
      <AppBar
        position="fixed"
        sx={{ zIndex: (t) => t.zIndex.drawer + 1 }}
        component="header"
      >
        <Toolbar>
          <Typography variant="h6" component="h1" sx={{ flexGrow: 1 }}>
            Accessible Climate Data Integration Platform
          </Typography>
          <Tooltip title="Cycle theme (Alt+T): Light / Dark / High Contrast">
            <IconButton color="inherit" onClick={cycleTheme} aria-label={`Cycle theme, current ${themeMode}`}>
              <Brightness4Icon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Increase font size (Alt+=)">
            <IconButton color="inherit" onClick={increaseFont} aria-label="Increase font size">
              <TextIncreaseIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Decrease font size (Alt+-)">
            <IconButton color="inherit" onClick={decreaseFont} aria-label="Decrease font size">
              <TextDecreaseIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title={colorBlind ? "Disable color-blind palette" : "Enable color-blind palette"}>
            <IconButton
              color="inherit"
              onClick={() => setColorBlind(!colorBlind)}
              aria-pressed={colorBlind}
              aria-label="Toggle color blind friendly charts"
            >
              <PaletteIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title={ttsEnabled ? "Disable voice narration" : "Enable voice narration"}>
            <IconButton
              color="inherit"
              onClick={() => setTtsEnabled(!ttsEnabled)}
              aria-pressed={ttsEnabled}
              aria-label="Toggle text to speech narration"
            >
              <RecordVoiceOverIcon />
            </IconButton>
          </Tooltip>
          <Typography variant="body2" sx={{ mx: 2 }} aria-label={`Logged in as ${user?.username}, role ${user?.role}`}>
            {user?.username} ({user?.role})
          </Typography>
          <Tooltip title="Log out">
            <IconButton color="inherit" onClick={handleLogout} aria-label="Log out">
              <LogoutIcon />
            </IconButton>
          </Tooltip>
        </Toolbar>
      </AppBar>

      <Drawer
        variant="permanent"
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          [`& .MuiDrawer-paper`]: { width: drawerWidth, boxSizing: "border-box" },
        }}
      >
        <Toolbar />
        <Box sx={{ overflow: "auto" }} component="nav" aria-label="Main navigation">
          <List>
            {NAV.map((item, i) => (
              <ListItemButton
                key={item.path}
                selected={location.pathname === item.path}
                onClick={() => {
                  navigate(item.path);
                  speakIfEnabled(item.label);
                }}
                aria-current={location.pathname === item.path ? "page" : undefined}
              >
                <ListItemIcon>{item.icon}</ListItemIcon>
                <ListItemText primary={item.label} secondary={`Alt+${i + 1}`} />
              </ListItemButton>
            ))}
          </List>
        </Box>
      </Drawer>

      <Box
        component="main"
        id="main-content"
        tabIndex={-1}
        sx={{ flexGrow: 1, p: 3, width: { sm: `calc(100% - ${drawerWidth}px)` } }}
      >
        <Toolbar />
        <Outlet />
      </Box>
    </Box>
  );
}
