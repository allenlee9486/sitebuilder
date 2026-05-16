import { Sword, Map as MapIcon, Shield, Database, ArrowRight } from "lucide-react";

export default function Home() {
  return (
    <div className="flex flex-col gap-16 pb-20">
      {/* Hero Section */}
      <section className="relative h-[600px] flex items-center justify-center overflow-hidden">
        <div className="absolute inset-0 z-0">
          <img 
            src="https://cdn.akamai.steamstatic.com/steam/apps/4466620/header.jpg" 
            alt="SiNiSistar 2 Hero" 
            className="w-full h-full object-cover opacity-30 blur-sm scale-105"
          />
          <div className="absolute inset-0 bg-gradient-to-b from-slate-950/20 via-slate-950/80 to-slate-950"></div>
        </div>
        
        <div className="container mx-auto px-4 relative z-10 text-center">
          <span className="inline-block px-3 py-1 rounded-full bg-red-500/10 text-red-500 text-xs font-bold uppercase tracking-widest mb-4 border border-red-500/20">
            Official Release Guide
          </span>
          <h1 className="text-5xl md:text-7xl font-extrabold mb-6 tracking-tight">
            Master the <span className="text-red-500">Darkness</span> in <br /> SiNiSistar 2
          </h1>
          <p className="text-xl text-slate-400 max-w-2xl mx-auto mb-10 leading-relaxed">
            The most comprehensive English resource for the decadent action-RPG. 
            Complete walkthroughs, interactive maps, and item databases.
          </p>
          <div className="flex flex-wrap gap-4 justify-center">
            <a href="/database" className="px-8 py-4 bg-red-600 hover:bg-red-700 rounded-lg font-bold transition-all flex items-center gap-2">
              Explore Database <ArrowRight size={18} />
            </a>
            <a href="/bosses" className="px-8 py-4 bg-slate-800 hover:bg-slate-700 rounded-lg font-bold transition-all">
              Boss Strategies
            </a>
          </div>
        </div>
      </section>

      {/* Quick Links Grid */}
      <section className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <FeatureCard 
            icon={<Database className="text-blue-500" />}
            title="Item Database"
            desc="Every weapon, relic, and magic spell cataloged with locations."
            href="/database"
          />
          <FeatureCard 
            icon={<MapIcon className="text-green-500" />}
            title="Interactive Maps"
            desc="Detailed maps for all 6 dungeons with secret locations."
            href="/maps"
          />
          <FeatureCard 
            icon={<Sword className="text-red-500" />}
            title="Boss Guide"
            desc="Weaknesses and patterns for every 'Abominable Child'."
            href="/bosses"
          />
          <FeatureCard 
            icon={<Shield className="text-purple-500" />}
            title="Relics List"
            desc="Track your collection and power up Sister Lelia."
            href="/relics"
          />
        </div>
      </section>

      {/* Latest Updates Section */}
      <section className="container mx-auto px-4 py-10">
        <h2 className="text-3xl font-bold mb-8 flex items-center gap-3">
          <div className="w-1 h-8 bg-red-500 rounded-full"></div>
          Trending Guides
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <GuidePreview 
            title="Magic System & Controls"
            desc="Learn how to master Arrow and Sword magic for maximum damage."
            href="/guides/magic-system"
          />
          <GuidePreview 
            title="All Endings Walkthrough"
            desc="Step-by-step guide to achieving all story outcomes."
            href="/guides/endings"
          />
          <GuidePreview 
            title="Scivias Powder Guide"
            desc="How to craft the essential powder to see the final boss."
            href="/guides/scivias-powder"
          />
        </div>
      </section>
    </div>
  );
}

function FeatureCard({ icon, title, desc, href }: any) {
  return (
    <a href={href} className="p-6 rounded-2xl bg-slate-900 border border-slate-800 hover:border-slate-700 hover:bg-slate-800/50 transition-all group">
      <div className="w-12 h-12 rounded-xl bg-slate-950 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
        {icon}
      </div>
      <h3 className="text-xl font-bold mb-2">{title}</h3>
      <p className="text-slate-400 text-sm leading-relaxed">{desc}</p>
    </a>
  );
}

function GuidePreview({ title, desc, href }: any) {
  return (
    <a href={href} className="block group">
      <div className="aspect-video rounded-xl bg-slate-900 mb-4 border border-slate-800 overflow-hidden relative">
        <div className="absolute inset-0 bg-slate-800 group-hover:bg-slate-700 transition-colors"></div>
        <div className="absolute inset-0 flex items-center justify-center text-slate-600 font-bold opacity-50">
          PREVIEW IMAGE
        </div>
      </div>
      <h3 className="text-lg font-bold group-hover:text-red-500 transition-colors mb-2">{title}</h3>
      <p className="text-slate-400 text-sm line-clamp-2">{desc}</p>
    </a>
  );
}
