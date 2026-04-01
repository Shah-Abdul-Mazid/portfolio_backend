import Analytics from '../models/Analytics.js';
import Visitor from '../models/Visitor.js';

export const trackPageView = async (req, res) => {
    try {
<<<<<<< HEAD
        const ip = req.headers['x-forwarded-for'] || req.socket.remoteAddress;
        const device = req.headers['user-agent'] || 'Unknown';

        // 1. Increment total views
        const result = await Analytics.findOneAndUpdate(
            { id: 'total_views' },
            { $inc: { count: 1 } },
            { upsert: true, new: true }
        );

        // 2. Clear existing visitor if same IP within last hour (to avoid spamming)
        // Or just log every visit if preferred. Let's log unique IPs per hour.
        const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000);
        const existingRecent = await Visitor.findOne({ ip, timestamp: { $gte: oneHourAgo } });

        if (!existingRecent) {
            await Visitor.create({ ip, device });
        }

        res.json(result);
=======
        const ip = req.headers['x-forwarded-for']?.split(',')[0] || 
                   req.headers['x-real-ip'] || 
                   req.socket.remoteAddress || 
                   req.ip;

        const device = req.headers['user-agent'] || 'Unknown Device';

        if (!ip) throw new Error('Could not identify visitor IP');

        const existingVisit = await Visitor.findOne({ ip });

        if (!existingVisit) {
            await Visitor.create({ ip, device });
            const result = await Analytics.findOneAndUpdate(
                { id: 'total_views' },
                { $inc: { count: 1 } },
                { upsert: true, new: true }
            );
            return res.status(201).json(result);
        }

        const currentStats = await Analytics.findOne({ id: 'total_views' });
        res.json(currentStats || { count: 0 });
>>>>>>> 9b08fa492481a48d1cd41d603af853dbd0c0c68e
    } catch (err) {
        console.error('Error tracking visit:', err.message);
        res.status(500).json({ error: 'Failed to track visit' });
    }
};

export const getAnalytics = async (req, res) => {
    try {
        const result = await Analytics.findOne({ id: 'total_views' });
        res.json(result || { count: 0 });
    } catch (err) {
        console.error('Error fetching analytics:', err.message);
        res.status(500).json({ error: 'Failed to fetch analytics' });
    }
};

<<<<<<< HEAD
export const getVisitors = async (req, res) => {
    try {
        const visitors = await Visitor.find().sort({ timestamp: -1 }).limit(50);
        res.json(visitors);
    } catch (err) {
        console.error('Error fetching visitors:', err.message);
        res.status(500).json({ error: 'Failed to fetch visitors' });
    }
};

export const clearAnalytics = async (req, res) => {
    try {
        await Analytics.updateOne({ id: 'total_views' }, { count: 0 });
        await Visitor.deleteMany({});
        res.json({ success: true, message: 'Analytics and Visitor logs cleared successfully' });
    } catch (err) {
        console.error('Error clearing analytics:', err.message);
        res.status(500).json({ error: 'Failed to clear analytics' });
=======
export const getVisitorsList = async (req, res) => {
    try {
        const visitors = await Visitor.find().sort({ timestamp: -1 });
        res.json(visitors);
    } catch (err) {
        res.status(500).json({ error: 'Failed to retrieve visitor log' });
    }
};

export const clearAllVisitors = async (req, res) => {
    try {
        await Visitor.deleteMany({});
        await Analytics.findOneAndUpdate({ id: 'total_views' }, { count: 0 });
        res.json({ success: true, message: 'All visitor records and view counts cleared.' });
    } catch (err) {
        res.status(500).json({ error: 'Failed to clear data' });
>>>>>>> 9b08fa492481a48d1cd41d603af853dbd0c0c68e
    }
};
