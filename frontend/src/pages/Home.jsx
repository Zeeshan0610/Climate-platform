import { Box, Typography } from "@mui/material";
import PublicIcon from "@mui/icons-material/Public";
import StorageIcon from "@mui/icons-material/Storage";
import ThermostatIcon from "@mui/icons-material/Thermostat";
import VerifiedIcon from "@mui/icons-material/Verified";
import DatasetIcon from "@mui/icons-material/Dataset";
import AccessibilityNewIcon from "@mui/icons-material/AccessibilityNew";
import HubIcon from "@mui/icons-material/Hub";
import { useEffect } from "react";
import StatCard from "../components/StatCard";
import { ErrorMessage, Loading } from "../components/Loading";
import useFetch from "../api/useFetch";
import { useAccessibility } from "../context/AccessibilityContext";

const grid = {
  display: "grid",
  gap: 2,
  gridTemplateColumns: { xs: "1fr", sm: "1fr 1fr", md: "repeat(4, 1fr)" },
};

export default function Home() {
  const { data, loading, error } = useFetch("/stats/home");
  const { speakIfEnabled } = useAccessibility();

  useEffect(() => {
    if (data) {
      speakIfEnabled(
        `Home dashboard. ${data.total_records} records across ${data.total_countries} countries. Data quality ${data.overall_quality_score} percent.`
      );
    }
  }, [data, speakIfEnabled]);

  if (loading) return <Loading />;
  if (error) return <ErrorMessage error={error} />;

  return (
    <Box>
      <Typography variant="h4" component="h2" gutterBottom>
        Platform Overview
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        An accessibility-aware framework that ingests, harmonizes and analyzes climate data from
        multiple heterogeneous repositories.
      </Typography>

      <Box sx={grid}>
        <StatCard title="Total Records" value={data.total_records.toLocaleString()} icon={<StorageIcon />} />
        <StatCard title="Total Countries" value={data.total_countries} icon={<PublicIcon />} />
        <StatCard title="Integrated Datasets" value={data.total_datasets} icon={<DatasetIcon />} />
        <StatCard
          title="Avg Temperature"
          value={data.average_temperature ?? "-"}
          unit="°C"
          icon={<ThermostatIcon />}
        />
      </Box>

      <Box sx={{ ...grid, mt: 2 }}>
        <StatCard title="Avg Rainfall" value={data.average_rainfall ?? "-"} unit="mm" icon={<ThermostatIcon />} />
        <StatCard title="Avg Humidity" value={data.average_humidity ?? "-"} unit="%" icon={<ThermostatIcon />} />
        <StatCard
          title="Data Quality Score"
          value={data.overall_quality_score}
          unit="%"
          icon={<VerifiedIcon />}
          color="success.main"
        />
        <StatCard
          title="Accessibility Score"
          value={data.accessibility_score}
          unit="%"
          icon={<AccessibilityNewIcon />}
          color="secondary.main"
        />
      </Box>

      <Box sx={{ ...grid, mt: 2 }}>
        <StatCard
          title="Interoperability Score"
          value={data.interoperability_score}
          unit="%"
          icon={<HubIcon />}
          color="info.main"
        />
      </Box>
    </Box>
  );
}
