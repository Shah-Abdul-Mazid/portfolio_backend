import express from 'express';
import { postMessage, getMessages, deleteMessage } from '../controllers/messageController.js';
import authMiddleware from '../middleware/authMiddleware.js';

const router = express.Router();

router.post('/', postMessage);
router.get('/', authMiddleware, getMessages);
router.delete('/:id', authMiddleware, deleteMessage);

export default router;
