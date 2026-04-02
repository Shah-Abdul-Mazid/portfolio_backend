import express from 'express';
import { trackPageView, getAnalytics, getVisitorsList, clearAllVisitors } from '../controllers/analyticsController.js';
import authMiddleware from '../middleware/authMiddleware.js';

const router = express.Router();

router.post('/track', trackPageView);
router.get('/', getAnalytics);
router.get('/visitors', authMiddleware, getVisitorsList);
router.post('/clear', authMiddleware, clearAllVisitors);

export default router;
