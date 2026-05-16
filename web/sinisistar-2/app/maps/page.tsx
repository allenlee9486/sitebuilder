import { Map as MapIcon, Info } from "lucide-react";

const dungeons = [
  {
    "name": "Alsezon Town",
    "type": "Hub",
    "features": ["Monastery (Save/Respec)", "Shop", "Tavern"]
  },
  {
    "name": "Blood-Drinking Swamp",
    "type": "Dungeon",
    "hazards": ["Deep Mud", "Leeches"],
    "key_items": ["Piercing Arrow", "Medical Leech"]
  },
  {
    "name": "Demi-human Base",
    "type": "Dungeon",
    "hazards": ["Prison Traps", "Ambush"],
    "key_items": ["Aspen Staff", "Owl Magic"]
  },
  {
    "name": "Northeast Village",
    "type": "Dungeon",
    "hazards": ["Parasites", "Mutants"],
    "key_items": ["Explosive Arrow", "Cathedral Key"]
  },
  {
    "name": "Body Cave",
    "type": "Dungeon",
    "hazards": ["Acid", "Tentacles"],
    "key_items": ["Relics Increase Item"]
  },
  {
    "name": "Alsezon Cathedral",
    "type": "Final Dungeon",
    "features": ["Library", "Archive", "Top Floor"]
  }
];

export default function MapsPage() {
  return (
    <div className="container mx-auto px-4 py-12">
      <div className="mb-12">
        <h1 className="text-4xl font-bold mb-4">World & Dungeon Maps</h1>
        <p className="text-slate-400">Detailed navigation for all major areas in Alsezon.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {dungeons.map((dungeon, idx) => (
          <div key={idx} className="bg-slate-900 border border-slate-800 rounded-2xl p-6 hover:border-slate-700 transition-all">
            <div className="flex justify-between items-start mb-6">
              <div>
                <h2 className="text-xl font-bold mb-1">{dungeon.name}</h2>
                <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-400 text-[10px] font-bold uppercase tracking-widest">
                  {dungeon.type}
                </span>
              </div>
              <div className="w-10 h-10 rounded-lg bg-slate-800 flex items-center justify-center text-slate-500">
                <MapIcon size={20} />
              </div>
            </div>

            <div className="space-y-4">
              <div className="aspect-video rounded-lg bg-slate-950 flex items-center justify-center text-slate-700 font-bold border border-slate-800">
                MAP PREVIEW COMING SOON
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h3 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2">Key Features</h3>
                  <ul className="text-xs text-slate-400 space-y-1">
                    {(dungeon.features || dungeon.hazards).map((item, i) => (
                      <li key={i} className="flex items-center gap-2">
                        <div className="w-1 h-1 bg-slate-600 rounded-full"></div>
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>
                <div>
                  <h3 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2">Major Drops/Items</h3>
                  <ul className="text-xs text-slate-400 space-y-1">
                    {(dungeon.key_items || []).length > 0 ? (
                      dungeon.key_items.map((item, i) => (
                        <li key={i} className="flex items-center gap-2 text-red-400/80">
                          <div className="w-1 h-1 bg-red-500/50 rounded-full"></div>
                          {item}
                        </li>
                      ))
                    ) : (
                      <li className="text-slate-600 italic">None listed</li>
                    )}
                  </ul>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-12 p-6 rounded-2xl bg-blue-500/5 border border-blue-500/10 flex gap-4">
        <Info className="text-blue-500 shrink-0" size={24} />
        <p className="text-sm text-blue-200/70 leading-relaxed">
          <strong>Interactive Map Feature:</strong> We are currently developing a full web-based interactive map for the Alsezon Cathedral. 
          Check back soon for high-resolution renders with precise item markers.
        </p>
      </div>
    </div>
  );
}
