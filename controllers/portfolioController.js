import PortfolioContent from '../models/PortfolioContent.js';
import { extractUploadPaths, deleteUploadFile } from '../utils/fileCleanup.js';

export const getPortfolioData = async (req, res) => {
    try {
        const doc = await PortfolioContent.findOne({ key: 'main' });
        if (!doc) return res.json(null);
        res.json(doc.data);
    } catch (err) {
        console.error('Error fetching portfolio data:', err.message);
        res.status(500).json({ error: 'Failed to fetch portfolio data' });
    }
};

export const savePortfolioData = async (req, res) => {
    try {
        // 1. Fetch old data before update for comparison
        const oldDoc = await PortfolioContent.findOne({ key: 'main' });
        const oldData = oldDoc ? oldDoc.data : {};
        const newData = req.body;

        // 2. Perform the update
        const doc = await PortfolioContent.findOneAndUpdate(
            { key: 'main' },
            { data: newData, updated_at: new Date() },
            { upsert: true, new: true }
        );

        // 3. Trigger Smart File Cleanup (after successful DB update)
        const oldPaths = extractUploadPaths(oldData);
        const newPaths = extractUploadPaths(newData);

        // Filter for paths that are in oldData but NOT in newData
        const deletedPaths = Array.from(oldPaths).filter(path => !newPaths.has(path));
        
        if (deletedPaths.length > 0) {
            console.log(`🧹 Triggered cleanup for ${deletedPaths.length} deleted items.`);
            deletedPaths.forEach(path => deleteUploadFile(path));
        }

        console.log('✅ Portfolio data saved to MongoDB');
        res.json({ success: true, updated_at: doc.updated_at, cleaned: deletedPaths.length });
    } catch (err) {
        console.error('Error saving portfolio data:', err.message);
        res.status(500).json({ error: 'Failed to save portfolio data' });
    }
};
