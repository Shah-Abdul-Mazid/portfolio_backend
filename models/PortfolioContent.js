import mongoose from 'mongoose';

const PortfolioContentSchema = new mongoose.Schema({
    key: { type: String, default: 'main', unique: true },
    data: { type: mongoose.Schema.Types.Mixed, required: true },
    updated_at: { type: Date, default: Date.now }
});

const PortfolioContent = mongoose.model('PortfolioContent', PortfolioContentSchema, process.env.atlas_COLLECTION_NAME3 || 'portfolio_content');
export default PortfolioContent;
