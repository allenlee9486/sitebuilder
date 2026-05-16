import { Skull, Target, Zap } from "lucide-react";

const bosses = [
  {
    "name": "Swamp Child (沼の忌み子)",
    "location": "Blood-Drinking Swamp",
    "weakness": "Fire/Explosive",
    "strategy": "Avoid swamp water to prevent sinking. Use ranged attacks to keep distance from its leech-like projectiles."
  },
  {
    "name": "Demi-human Child (亜人の忌み子)",
    "location": "Demi-human Base",
    "weakness": "Magic",
    "strategy": "Fast movements. Watch for the 'Impregnation' status attack. Use Sword Magic for high burst damage when it pauses."
  },
  {
    "name": "Mock Spawn (模造の落とし子)",
    "location": "Northeast Village",
    "weakness": "Physical",
    "strategy": "High defense. Use Explosive Arrows to break its posture before attacking."
  },
  {
    "name": "Stomach Child (胃の忌み子)",
    "location": "Body Cave",
    "weakness": "Magic",
    "strategy": "Complex environment with tentacles. Use Owl Magic to stay airborne and avoid floor hazards."
  },
  {
    "name": "The Outer One (外なる者)",
    "location": "Cathedral Top",
    "weakness": "Scivias Powder",
    "strategy": "Must use Scivias Powder to see the true form. Manage MP carefully as it has high HP and multiple phases."
  }
];

export default function BossesPage() {
  return (
    <div className="container mx-auto px-4 py-12">
      <div className="mb-12">
        <h1 className="text-4xl font-bold mb-4">Boss Strategy Guide</h1>
        <p className="text-slate-400">Detailed weaknesses and tactics for every 'Abominable Child' in SiNiSistar 2.</p>
      </div>

      <div className="grid grid-cols-1 gap-10">
        {bosses.map((boss, idx) => (
          <div key={idx} className="bg-slate-900 border border-slate-800 rounded-3xl overflow-hidden flex flex-col md:flex-row">
            <div className="md:w-1/3 bg-slate-800 aspect-video md:aspect-auto flex items-center justify-center relative">
              <Skull size={64} className="text-slate-700 opacity-20" />
              <div className="absolute inset-0 bg-gradient-to-r from-transparent to-slate-900/50"></div>
            </div>
            <div className="p-8 flex-1">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h2 className="text-2xl font-bold mb-1 text-red-500">{boss.name}</h2>
                  <p className="text-slate-400 text-sm flex items-center gap-2">
                    <Target size={14} /> {boss.location}
                  </p>
                </div>
                <div className="px-3 py-1 rounded bg-red-500/10 text-red-500 text-xs font-bold border border-red-500/20 uppercase">
                  Abominable Child
                </div>
              </div>
              
              <div className="mb-6">
                <h3 className="text-sm font-bold text-slate-500 uppercase tracking-widest mb-2 flex items-center gap-2">
                  <Zap size={14} className="text-yellow-500" /> Primary Weakness
                </h3>
                <p className="text-yellow-500 font-medium">{boss.weakness}</p>
              </div>

              <div>
                <h3 className="text-sm font-bold text-slate-500 uppercase tracking-widest mb-2">Combat Strategy</h3>
                <p className="text-slate-300 leading-relaxed italic border-l-2 border-slate-700 pl-4">
                  "{boss.strategy}"
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
