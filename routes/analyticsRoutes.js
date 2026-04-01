import express from 'express';
import { trackPageView, getAnalytics, getVisitors, clearAnalytics } from '../controllers/analyticsController.js';

const router = express.Router();

router.post('/track', trackPageView);
router.get('/', getAnalytics);
router.get('/visitors', getVisitors);
router.post('/clear', clearAnalytics);

export default router;
