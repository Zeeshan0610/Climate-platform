import { Alert, Box, CircularProgress } from "@mui/material";

export function Loading({ label = "Loading data" }) {
  return (
    <Box sx={{ display: "flex", justifyContent: "center", p: 4 }} role="status" aria-live="polite">
      <CircularProgress aria-label={label} />
    </Box>
  );
}

export function ErrorMessage({ error }) {
  return (
    <Alert severity="error" role="alert" sx={{ my: 2 }}>
      {String(error)}
    </Alert>
  );
}
