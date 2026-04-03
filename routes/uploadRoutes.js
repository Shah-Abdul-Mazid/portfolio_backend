import express from 'express';
import multer from 'multer';
import mongoose from 'mongoose';
import path from 'path';
import { Readable } from 'stream';

const router = express.Router();

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

// Helper to get GridFS bucket — uses mongoose's bundled mongodb driver to avoid BSON version conflicts
const getBucket = () => {
    const db = mongoose.connection.db;
    if (!db) throw new Error('Database not connected');
    return new mongoose.mongo.GridFSBucket(db, { bucketName: 'uploads' });
};

// POST /api/upload — upload file to MongoDB GridFS
router.post('/', upload.single('file'), async (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({ success: false, message: 'No file uploaded' });
        }

        const bucket = getBucket();
        const uniqueName = `${Date.now()}-${Math.round(Math.random() * 1E9)}${path.extname(req.file.originalname)}`;

        // Create a readable stream from the buffer
        const readableStream = new Readable();
        readableStream.push(req.file.buffer);
        readableStream.push(null);

        // Upload to GridFS
        const uploadStream = bucket.openUploadStream(uniqueName, {
            contentType: req.file.mimetype,
            metadata: {
                originalName: req.file.originalname,
                uploadedAt: new Date()
            }
        });

        readableStream.pipe(uploadStream);

        uploadStream.on('finish', () => {
            const fileUrl = `/api/upload/${uploadStream.id}`;
            res.json({
                success: true,
                message: 'File uploaded successfully',
                url: fileUrl,
                fileId: uploadStream.id.toString(),
                filename: uniqueName
            });
        });

        uploadStream.on('error', (err) => {
            console.error('GridFS upload error:', err);
            res.status(500).json({ success: false, message: 'Upload failed' });
        });

    } catch (error) {
        console.error('Upload error:', error);
        res.status(500).json({ success: false, message: error.message });
    }
});

// GET /api/upload/:id — serve file from GridFS
router.get('/:id', async (req, res) => {
    try {
        const bucket = getBucket();
        let fileId;
        
        try {
            fileId = new mongoose.Types.ObjectId(req.params.id);
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

// DELETE /api/upload/:id — remove file from GridFS
router.delete('/:id', async (req, res) => {
    try {
        const bucket = getBucket();
        let fileId;
        
        try {
            fileId = new mongoose.Types.ObjectId(req.params.id);
        } catch (e) {
            return res.status(400).json({ success: false, message: 'Invalid file ID' });
        }

        await bucket.delete(fileId);
        res.json({ success: true, message: 'File deleted' });

    } catch (error) {
        console.error('File delete error:', error);
        res.status(500).json({ success: false, message: error.message });
    }
});

export default router;
