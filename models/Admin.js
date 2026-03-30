import mongoose from 'mongoose';

const AdminSchema = new mongoose.Schema({
    email: { type: String, required: true, unique: true },
    password: { type: String, required: true },
    role: { type: String, default: 'superadmin' },
    created_at: { type: Date, default: Date.now }
});

const Admin = mongoose.model('Admin', AdminSchema, process.env.atlas_COLLECTION_NAME1 || 'admin_db');
export default Admin;
