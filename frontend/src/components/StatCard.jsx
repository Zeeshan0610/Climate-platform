import { Box, Card, CardContent, Typography } from "@mui/material";

export default function StatCard({ title, value, unit, icon, color = "primary.main" }) {
  return (
    <Card sx={{ height: "100%" }} role="group" aria-label={`${title}: ${value} ${unit || ""}`}>
      <CardContent>
        <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1 }}>
          {icon && <Box sx={{ color }}>{icon}</Box>}
          <Typography variant="subtitle2" color="text.secondary" component="h3">
            {title}
          </Typography>
        </Box>
        <Typography variant="h4" component="p">
          {value}
          {unit && (
            <Typography component="span" variant="h6" color="text.secondary">
              {" "}
              {unit}
            </Typography>
          )}
        </Typography>
      </CardContent>
    </Card>
  );
}
