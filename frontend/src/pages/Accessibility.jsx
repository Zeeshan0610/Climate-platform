import {
  Box,
  Button,
  Card,
  CardContent,
  CardHeader,
  Chip,
  FormControlLabel,
  LinearProgress,
  Stack,
  Switch,
  Typography,
} from "@mui/material";
import useFetch from "../api/useFetch";
import StatCard from "../components/StatCard";
import { ErrorMessage, Loading } from "../components/Loading";
import { useAccessibility } from "../context/AccessibilityContext";

function PrincipleBar({ label, score, criteria }) {
  return (
    <Box sx={{ mb: 2 }}>
      <Box sx={{ display: "flex", justifyContent: "space-between" }}>
        <Typography variant="subtitle1" component="h4">
          {label}
        </Typography>
        <Typography variant="subtitle1">{score}%</Typography>
      </Box>
      <LinearProgress
        variant="determinate"
        value={score}
        aria-label={`${label} score ${score} percent`}
        sx={{ height: 10, borderRadius: 5 }}
      />
      <Typography variant="caption" color="text.secondary">
        {criteria}
      </Typography>
    </Box>
  );
}

export default function Accessibility() {
  const { data, loading, error } = useFetch("/accessibility-score");
  const {
    themeMode,
    cycleTheme,
    fontScale,
    increaseFont,
    decreaseFont,
    resetFont,
    colorBlind,
    setColorBlind,
    ttsEnabled,
    setTtsEnabled,
    speak,
  } = useAccessibility();

  if (loading) return <Loading />;
  if (error) return <ErrorMessage error={error} />;

  return (
    <Box>
      <Typography variant="h4" component="h2" gutterBottom>
        Accessibility (WCAG {data.wcag_level})
      </Typography>

      <Box sx={{ display: "grid", gap: 2, gridTemplateColumns: { xs: "1fr", md: "1fr 2fr" }, mb: 3 }}>
        <StatCard title="Overall Accessibility Score" value={data.overall_score} unit="%" color="secondary.main" />
        <Card>
          <CardHeader
            title="WCAG 2.1 Principles (POUR)"
            titleTypographyProps={{ variant: "h6", component: "h3" }}
          />
          <CardContent>
            {Object.values(data.principles).map((p) => (
              <PrincipleBar key={p.label} label={p.label} score={p.score} criteria={p.criteria} />
            ))}
          </CardContent>
        </Card>
      </Box>

      <Card sx={{ mb: 3 }}>
        <CardHeader
          title="Live Accessibility Controls"
          titleTypographyProps={{ variant: "h6", component: "h3" }}
        />
        <CardContent>
          <Stack spacing={2}>
            <Box>
              <Typography component="span" sx={{ mr: 2 }}>
                Theme: <strong>{themeMode}</strong>
              </Typography>
              <Button variant="outlined" onClick={cycleTheme}>
                Cycle Theme (Light / Dark / High Contrast)
              </Button>
            </Box>
            <Box sx={{ display: "flex", alignItems: "center", gap: 1, flexWrap: "wrap" }}>
              <Typography component="span">Font scale: {fontScale.toFixed(1)}x</Typography>
              <Button variant="outlined" onClick={decreaseFont}>
                A-
              </Button>
              <Button variant="outlined" onClick={increaseFont}>
                A+
              </Button>
              <Button variant="text" onClick={resetFont}>
                Reset
              </Button>
            </Box>
            <FormControlLabel
              control={<Switch checked={colorBlind} onChange={(e) => setColorBlind(e.target.checked)} />}
              label="Color-blind friendly chart palette"
            />
            <FormControlLabel
              control={<Switch checked={ttsEnabled} onChange={(e) => setTtsEnabled(e.target.checked)} />}
              label="Voice narration (text-to-speech)"
            />
            <Box>
              <Button
                variant="contained"
                onClick={() =>
                  speak(
                    `This platform meets WCAG ${data.wcag_level} with an overall accessibility score of ${data.overall_score} percent. It ships ${data.features_count} accessibility features.`
                  )
                }
              >
                Read Accessibility Summary Aloud
              </Button>
            </Box>
          </Stack>
        </CardContent>
      </Card>

      <Card>
        <CardHeader
          title={`Implemented Accessibility Features (${data.features_count})`}
          titleTypographyProps={{ variant: "h6", component: "h3" }}
        />
        <CardContent>
          <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
            {data.features.map((f) => (
              <Chip key={f} label={f} color="primary" variant="outlined" />
            ))}
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
}
