import express from 'express';
import { trackPageView, getAnalytics } from '../controllers/analyticsController.js';

const router = express.Router();

router.post('/track', trackPageView);
router.get('/', getAnalytics);

export default router;
