import express from 'express';
import { loginAdmin, registerAdmin, listAdmins } from '../controllers/adminController.js';
import authMiddleware from '../middleware/authMiddleware.js';

const router = express.Router();

router.post('/login', loginAdmin);
router.post('/register', authMiddleware, registerAdmin);
router.get('/list', authMiddleware, listAdmins);

export default router;
