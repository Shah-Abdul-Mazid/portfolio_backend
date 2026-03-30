import Admin from '../models/Admin.js';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';

export const loginAdmin = async (req, res) => {
    try {
        const { email, password } = req.body;
        console.log(`Login attempt for: ${email}`);
        
        const admin = await Admin.findOne({ email });
        if (!admin) {
            return res.status(401).json({ success: false, message: 'Invalid email or password' });
        }

        const isMatch = await bcrypt.compare(password, admin.password);
        if (!isMatch) {
            return res.status(401).json({ success: false, message: 'Invalid email or password' });
        }

        const token = jwt.sign(
            { id: admin._id, email: admin.email, role: admin.role },
            process.env.JWT_SECRET || 'secret',
            { expiresIn: '24h' }
        );

        res.json({ success: true, token, admin: { email: admin.email, role: admin.role } });
    } catch (error) {
        console.error('Login error:', error);
        res.status(500).json({ success: false, message: 'Server error' });
    }
};

export const registerAdmin = async (req, res) => {
    try {
        const { email, password } = req.body;

        const existing = await Admin.findOne({ email });
        if (existing) {
            return res.status(400).json({ success: false, message: 'Admin with this email already exists' });
        }

        const salt = await bcrypt.genSalt(10);
        const hashedPassword = await bcrypt.hash(password, salt);

        const newAdmin = new Admin({ email, password: hashedPassword });
        await newAdmin.save();

        res.json({ success: true, message: 'Admin created successfully' });
    } catch (error) {
        console.error('Register error:', error);
        res.status(500).json({ success: false, message: 'Server error' });
    }
};

export const listAdmins = async (req, res) => {
    try {
        const admins = await Admin.find({}, '-password').sort({ created_at: -1 });
        res.json({ success: true, data: admins });
    } catch (error) {
        console.error('List admins error:', error);
        res.status(500).json({ success: false, message: 'Server error' });
    }
};
