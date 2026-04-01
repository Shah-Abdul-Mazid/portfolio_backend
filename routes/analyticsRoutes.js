import express from 'express';
import { trackPageView, getAnalytics, getVisitorsList, clearAllVisitors } from '../controllers/analyticsController.js';

const router = express.Router();

router.post('/track', trackPageView);
router.get('/', getAnalytics);
router.get('/visitors', getVisitorsList);
router.post('/clear', clearAllVisitors);

export default router;
