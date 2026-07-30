import { FileText, Download, FileSpreadsheet, File, Search, Filter } from 'lucide-react';

const mockReports = [
  { id: 'REP-001', title: 'Global Supply Chain Disruption Summary', date: '2026-07-30', type: 'Executive Summary', status: 'Generated' },
  { id: 'REP-002', title: 'Q2 Risk Matrix & Mitigation Strategies', date: '2026-07-28', type: 'Risk Matrix', status: 'Generated' },
  { id: 'REP-003', title: 'Cyber Threat Analysis - APAC Region', date: '2026-07-25', type: 'Technical Audit', status: 'Generated' },
  { id: 'REP-004', title: 'Competitor Pricing Aggregation (Weekly)', date: '2026-07-21', type: 'Market Data', status: 'Generated' },
];

export function Reports() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end border-b border-border pb-4">
        <div>
          <h1 className="text-3xl font-bold text-foreground tracking-tight flex items-center gap-3">
            <FileText className="w-8 h-8 text-primary" />
            Executive Reports
          </h1>
          <p className="text-muted-foreground mt-1">Download and view AI-generated briefings, risk matrices, and timelines.</p>
        </div>
        <div className="flex gap-3">
          <button className="bg-primary hover:bg-primary/90 text-primary-foreground px-4 py-2 rounded-lg text-sm font-medium transition-colors shadow-[0_0_15px_rgba(37,99,235,0.2)]">
            Generate New Report
          </button>
        </div>
      </div>

      <div className="flex flex-col md:flex-row gap-4 justify-between items-center bg-card/50 backdrop-blur-sm border border-border p-4 rounded-xl">
        <div className="relative w-full md:w-96">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <input 
            type="text" 
            placeholder="Search reports by ID, title, or date..." 
            className="w-full bg-secondary/50 border border-border rounded-lg pl-10 pr-4 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary transition-all text-foreground placeholder:text-muted-foreground"
          />
        </div>
        <div className="flex gap-3 w-full md:w-auto">
          <button className="flex-1 md:flex-none bg-secondary hover:bg-secondary/80 text-foreground px-4 py-2 rounded-lg text-sm font-medium transition-colors border border-border flex items-center justify-center gap-2">
            <Filter className="w-4 h-4" /> Filter
          </button>
        </div>
      </div>

      <div className="bg-card/50 backdrop-blur-sm border border-border rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-secondary/40 border-b border-border text-xs uppercase tracking-wider text-muted-foreground font-semibold">
                <th className="p-4">Report ID</th>
                <th className="p-4">Title</th>
                <th className="p-4">Date Generated</th>
                <th className="p-4">Type</th>
                <th className="p-4 text-right">Downloads</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {mockReports.map((report) => (
                <tr key={report.id} className="hover:bg-secondary/20 transition-colors group">
                  <td className="p-4 font-mono text-sm text-primary">{report.id}</td>
                  <td className="p-4 font-medium text-foreground">{report.title}</td>
                  <td className="p-4 text-sm text-muted-foreground">{report.date}</td>
                  <td className="p-4">
                    <span className="bg-secondary text-foreground text-xs px-2.5 py-1 rounded-md border border-border font-medium">
                      {report.type}
                    </span>
                  </td>
                  <td className="p-4 flex items-center justify-end gap-2 opacity-70 group-hover:opacity-100 transition-opacity">
                    <button className="p-2 bg-secondary hover:bg-primary/20 hover:text-primary rounded-lg transition-colors border border-transparent hover:border-primary/30" title="Download PDF">
                      <File className="w-4 h-4" />
                    </button>
                    <button className="p-2 bg-secondary hover:bg-emerald-500/20 hover:text-emerald-500 rounded-lg transition-colors border border-transparent hover:border-emerald-500/30" title="Download Excel">
                      <FileSpreadsheet className="w-4 h-4" />
                    </button>
                    <button className="p-2 bg-secondary hover:bg-amber-500/20 hover:text-amber-500 rounded-lg transition-colors border border-transparent hover:border-amber-500/30" title="Download DOCX">
                      <Download className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
