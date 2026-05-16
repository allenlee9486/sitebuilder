import { Shield, MapPin, Sparkles } from "lucide-react";

const relics = [
  {
    "name": "Staurotheka",
    "location": "Alsezon Cathedral (Archive)",
    "effect": "Increases the amount of Relics obtained during exploration.",
    "howToGet": "Locate the archive elevator, step off to the right side during the descent to find a hidden ledge."
  },
  {
    "name": "Medical Leech",
    "location": "Blood-Drinking Swamp",
    "effect": "Used at the Monastery to treat the 'Bust Expansion' status.",
    "howToGet": "Found in a chest guarded by multiple Leeches in the second area of the swamp."
  },
  {
    "name": "Vision Scivias",
    "location": "Alsezon Cathedral (Archive)",
    "effect": "Essential book for crafting the Scivias Powder.",
    "howToGet": "Obtained automatically during the story quest in the Cathedral Library."
  }
];

export default function RelicsPage() {
  return (
    <div className="container mx-auto px-4 py-12">
      <div className="mb-12">
        <h1 className="text-4xl font-bold mb-4 text-purple-500">Relics & Collection</h1>
        <p className="text-slate-400">Track and find all hidden relics to strengthen Sister Lelia's purification powers.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {relics.map((relic, idx) => (
          <div key={idx} className="bg-slate-900 border border-slate-800 rounded-2xl p-6 relative group overflow-hidden">
            <div className="absolute top-0 right-0 w-24 h-24 bg-purple-500/10 rounded-full -mr-12 -mt-12 group-hover:scale-150 transition-transform duration-500"></div>
            
            <div className="w-12 h-12 rounded-xl bg-purple-500/10 flex items-center justify-center text-purple-500 mb-6">
              <Shield size={24} />
            </div>

            <h2 className="text-xl font-bold mb-4">{relic.name}</h2>
            
            <div className="space-y-4 relative z-10">
              <div className="flex gap-3">
                <MapPin className="text-slate-500 shrink-0" size={16} />
                <p className="text-sm text-slate-300 font-medium">{relic.location}</p>
              </div>
              
              <div className="flex gap-3">
                <Sparkles className="text-yellow-500 shrink-0" size={16} />
                <p className="text-xs text-slate-400 leading-relaxed">{relic.effect}</p>
              </div>

              <div className="pt-4 border-t border-slate-800">
                <h3 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2">How to Obtain</h3>
                <p className="text-[11px] text-slate-500 italic">{relic.howToGet}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
