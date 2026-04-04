import express from 'express';
import multer from 'multer';
import mongoose from 'mongoose';
import path from 'path';
import { Readable } from 'stream';
import { v2 as cloudinary } from 'cloudinary';
import dotenv from 'dotenv';

dotenv.config();

const router = express.Router();

// Cloudinary Configuration
cloudinary.config({
    cloud_name: process.env.CLOUDINARY_CLOUD_NAME,
    api_key: process.env.CLOUDINARY_API_KEY,
    api_secret: process.env.CLOUDINARY_API_SECRET
});

// Use multer memory storage (no disk writes — works on Vercel/Render)
const upload = multer({
    storage: multer.memoryStorage(),
    limits: { fileSize: 10 * 1024 * 1024 }, // 10MB limit
    fileFilter: (req, file, cb) => {
        const allowedTypes = /jpeg|jpg|png|pdf/;
        const extname = allowedTypes.test(path.extname(file.originalname).toLowerCase());
        const mimetype = allowedTypes.test(file.mimetype);
        if (extname && mimetype) {
            return cb(null, true);
        } else {
            cb(new Error('Only Images (JPG, PNG) and PDFs are allowed'));
        }
    }
});

/**
 * Upload buffer to Cloudinary using a Promise
 */
const uploadToCloudinary = (fileBuffer, originalName) => {
    return new Promise((resolve, reject) => {
        const uploadStream = cloudinary.uploader.upload_stream(
            {
                resource_type: 'auto',
                folder: 'portfolio_uploads',
                public_id: `${path.parse(originalName).name}-${Date.now()}`
            },
            (error, result) => {
                if (error) reject(error);
                else resolve(result);
            }
        );

        const readableStream = new Readable();
        readableStream.push(fileBuffer);
        readableStream.push(null);
        readableStream.pipe(uploadStream);
    });
};

// Helper to get GridFS bucket (Legacy Support)
const getBucket = () => {
    const db = mongoose.connection.db;
    if (!db) throw new Error('Database not connected');
    return new mongoose.mongo.GridFSBucket(db, { bucketName: 'uploads' });
};

// POST /api/upload — upload file to Cloudinary
router.post('/', upload.single('file'), async (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({ success: false, message: 'No file uploaded' });
        }

        // Perform the upload to Cloudinary
        const result = await uploadToCloudinary(req.file.buffer, req.file.originalname);

        res.json({
            success: true,
            message: 'File uploaded successfully to Cloudinary',
            url: result.secure_url, // Full Cloudinary HTTPS URL
            public_id: result.public_id,
            filename: req.file.originalname
        });

    } catch (error) {
        console.error('Cloudinary upload error:', error);
        res.status(500).json({ success: false, message: 'Cloudinary upload failed: ' + error.message });
    }
});

// GET /api/upload/:id — serve file from GridFS (LEGACY - keep for old links)
router.get('/:id', async (req, res) => {
    try {
        const bucket = getBucket();
        let fileId;
        
        try {
            const rawId = req.params.id.split('.')[0];
            fileId = new mongoose.Types.ObjectId(rawId);
        } catch (e) {
            return res.status(400).json({ success: false, message: 'Invalid file ID' });
        }

        // Find file metadata
        const files = await bucket.find({ _id: fileId }).toArray();
        if (!files || files.length === 0) {
            return res.status(404).json({ success: false, message: 'File not found' });
        }

        const file = files[0];

        // Set proper headers
        res.set('Content-Type', file.contentType || 'application/octet-stream');
        res.set('Content-Disposition', `inline; filename="${file.filename}"`);
        res.set('Cache-Control', 'public, max-age=31536000, immutable');

        // Stream file to response
        const downloadStream = bucket.openDownloadStream(fileId);
        downloadStream.pipe(res);

        downloadStream.on('error', (err) => {
            console.error('GridFS download error:', err);
            if (!res.headersSent) {
                res.status(500).json({ success: false, message: 'Error reading file' });
            }
        });

    } catch (error) {
        console.error('File serve error:', error);
        res.status(500).json({ success: false, message: error.message });
    }
});

// DELETE /api/upload/:id — remove file (Supports both GridFS and Cloudinary)
router.delete('/:id', async (req, res) => {
    try {
        const idOrUrl = req.params.id;

        // If it's a Cloudinary public ID, we'd need to handle it.
        // For now, let's keep it simple or expand if needed.
        // The fileCleanup utility below handles deletions from the DB updates.
        
        const bucket = getBucket();
        let fileId;
        
        try {
            const rawId = idOrUrl.split('.')[0];
            fileId = new mongoose.Types.ObjectId(rawId);
            await bucket.delete(fileId);
            return res.json({ success: true, message: 'Legacy GridFS file deleted' });
        } catch (e) {
            // Probably not a GridFS ID, maybe Cloudinary or something else.
            res.status(400).json({ success: false, message: 'Invalid or non-GridFS file ID' });
        }

    } catch (error) {
        console.error('File delete error:', error);
        res.status(500).json({ success: false, message: error.message });
    }
});

export default router;

