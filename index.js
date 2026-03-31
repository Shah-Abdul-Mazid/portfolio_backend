import express from 'express';
import dotenv from 'dotenv';
import cors from 'cors';
import path from 'path';
import { fileURLToPath } from 'url';

// Import Custom Config & Routes
import connectDB from './config/db.js';
import portfolioRoutes from './routes/portfolioRoutes.js';
import messageRoutes from './routes/messageRoutes.js';
import adminRoutes from './routes/adminRoutes.js';
import analyticsRoutes from './routes/analyticsRoutes.js';

// Fix __dirname for ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load env variables
dotenv.config();

const app = express();
const port = process.env.PORT || 3001;

// ── MIDDLEWARE ────────────────────────────────────────────
app.use(cors());
app.use(express.json()); // replaces body-parser

// ── DATABASE CONNECTION ───────────────────────────────────
connectDB();

// ── HEALTH & BASE ROUTES (IMPORTANT FOR RENDER + CRON) ────

// Base route
app.get('/', (req, res) => {
    res.status(200).send('🚀 Backend is running successfully');
});

// Health check route (used for cron job)
app.get('/health', (req, res) => {
    console.log('✅ Ping received at:', new Date().toISOString());
    res.status(200).send('OK');
});

// ── API ROUTES ────────────────────────────────────────────
app.use('/api/portfolio', portfolioRoutes);
app.use('/api/messages', messageRoutes);
app.use('/api/admin', adminRoutes);
app.use('/api/analytics', analyticsRoutes);

// ── ERROR HANDLING ────────────────────────────────────────
process.on('unhandledRejection', (reason, promise) => {
    console.error('❌ Unhandled Rejection at:', promise, 'reason:', reason);
});

process.on('uncaughtException', (err) => {
    console.error('❌ Uncaught Exception:', err);
});

// Optional: Express error handler middleware
app.use((err, req, res, next) => {
    console.error('🔥 Server Error:', err.stack);
    res.status(500).json({ message: 'Internal Server Error' });
});

// ── SERVER START ──────────────────────────────────────────
app.listen(port, '0.0.0.0', () => {
    console.log(`🚀 Server running on port ${port}`);
    console.log(`🌐 http://localhost:${port}`);
});

export default app;
