import express from 'express';
import { postMessage, getMessages, deleteMessage } from '../controllers/messageController.js';

const router = express.Router();

router.post('/', postMessage);
router.get('/', getMessages);
router.delete('/:id', deleteMessage);

export default router;
