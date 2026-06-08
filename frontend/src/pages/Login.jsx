import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("admin123");
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const onSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await login(username, password);
      navigate("/");
    } catch (err) {
      setError(err?.response?.data?.detail || "Login failed");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Box
      component="main"
      sx={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        bgcolor: "background.default",
        p: 2,
      }}
    >
      <Card sx={{ maxWidth: 420, width: "100%" }}>
        <CardContent>
          <Typography variant="h5" component="h1" gutterBottom>
            Climate Data Platform
          </Typography>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Sign in to access accessible climate analytics.
          </Typography>
          <form onSubmit={onSubmit} aria-label="Login form">
            <Stack spacing={2} sx={{ mt: 2 }}>
              {error && (
                <Alert severity="error" role="alert">
                  {error}
                </Alert>
              )}
              <TextField
                label="Username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                autoFocus
                fullWidth
                inputProps={{ "aria-label": "Username" }}
              />
              <TextField
                label="Password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                fullWidth
                inputProps={{ "aria-label": "Password" }}
              />
              <Button type="submit" variant="contained" size="large" disabled={submitting}>
                {submitting ? "Signing in..." : "Sign In"}
              </Button>
              <Typography variant="caption" color="text.secondary">
                Demo accounts: admin/admin123 · analyst/analyst123 · viewer/viewer123
              </Typography>
            </Stack>
          </form>
        </CardContent>
      </Card>
    </Box>
  );
}
