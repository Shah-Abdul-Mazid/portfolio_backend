import express from 'express';
import { getPortfolioData, savePortfolioData } from '../controllers/portfolioController.js';
import authMiddleware from '../middleware/authMiddleware.js';

const router = express.Router();

router.get('/', getPortfolioData);
router.post('/', authMiddleware, savePortfolioData);

export default router;
