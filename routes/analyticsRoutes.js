import express from 'express';
<<<<<<< HEAD
import { trackPageView, getAnalytics, getVisitors, clearAnalytics } from '../controllers/analyticsController.js';
=======
import { trackPageView, getAnalytics, getVisitorsList, clearAllVisitors } from '../controllers/analyticsController.js';
>>>>>>> 9b08fa492481a48d1cd41d603af853dbd0c0c68e

const router = express.Router();

router.post('/track', trackPageView);
router.get('/', getAnalytics);
<<<<<<< HEAD
router.get('/visitors', getVisitors);
router.post('/clear', clearAnalytics);
=======
router.get('/visitors', getVisitorsList);
router.post('/clear', clearAllVisitors);
>>>>>>> 9b08fa492481a48d1cd41d603af853dbd0c0c68e

export default router;
