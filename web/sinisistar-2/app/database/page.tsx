import { Search, Filter } from "lucide-react";

const items = [
  {
    "name": "Arrow Magic",
    "category": "Magic",
    "location": "Initial",
    "effect": "Standard ranged attack."
  },
  {
    "name": "Sword Magic",
    "category": "Magic",
    "location": "Initial",
    "effect": "Standard melee magic attack."
  },
  {
    "name": "Piercing Arrow Magic",
    "category": "Magic",
    "location": "Blood-Drinking Swamp",
    "effect": "Arrows penetrate enemies."
  },
  {
    "name": "Explosive Arrow Magic",
    "category": "Magic",
    "location": "Northeast Village (Before Boss)",
    "effect": "Arrows can be detonated with Sword Magic. Breaks defenses and meat blocks."
  },
  {
    "name": "Owl Magic",
    "category": "Magic",
    "location": "Demi-human Base (SE dead end)",
    "effect": "Hold jump button to hover in the air."
  },
  {
    "name": "Yew Staff",
    "category": "Weapon",
    "location": "Initial",
    "effect": "Standard staff."
  },
  {
    "name": "Staff of Suffering",
    "category": "Weapon",
    "location": "South Road Swamp",
    "effect": "Disables level-up effects while equipped."
  },
  {
    "name": "Aspen Staff",
    "category": "Weapon",
    "location": "Demi-human Base",
    "effect": "Magic Attack +2."
  },
  {
    "name": "Exorcism Staff Sword",
    "category": "Weapon",
    "location": "Alsezon Town (Shop)",
    "effect": "Magic Attack +3, Physical Attack +1."
  },
  {
    "name": "Tranquebal",
    "category": "Weapon",
    "location": "West Road (Use Scivias Powder between pillars)",
    "effect": "Magic Attack +5, Physical Attack +1, MP Consumption -3."
  },
  {
    "name": "Staurotheka",
    "category": "Relic",
    "location": "Cathedral Archive (Fall from lift)",
    "effect": "Increases Relics obtained while held."
  },
  {
    "name": "Scivias Powder",
    "category": "Key Item",
    "location": "Crafted (Archive materials)",
    "effect": "Allows player to see invisible higher entities (Final Boss, Seere, etc.)."
  }
];

export default function DatabasePage() {
  return (
    <div className="container mx-auto px-4 py-12">
      <div className="mb-12">
        <h1 className="text-4xl font-bold mb-4">Item Database</h1>
        <p className="text-slate-400">Comprehensive list of weapons, magic spells, and relics in SiNiSistar 2.</p>
      </div>

      {/* Search & Filter Bar */}
      <div className="flex flex-col md:flex-row gap-4 mb-8">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
          <input 
            type="text" 
            placeholder="Search items..." 
            className="w-full bg-slate-900 border border-slate-800 rounded-lg py-3 pl-10 pr-4 focus:outline-none focus:border-red-500 transition-colors"
          />
        </div>
        <div className="flex gap-2">
          <button className="px-4 py-2 bg-slate-800 rounded-lg text-sm font-medium hover:bg-slate-700 transition-colors flex items-center gap-2">
            <Filter size={16} /> Category
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-slate-950/50 border-b border-slate-800">
              <th className="px-6 py-4 font-bold text-sm uppercase tracking-wider">Name</th>
              <th className="px-6 py-4 font-bold text-sm uppercase tracking-wider">Category</th>
              <th className="px-6 py-4 font-bold text-sm uppercase tracking-wider">Location</th>
              <th className="px-6 py-4 font-bold text-sm uppercase tracking-wider">Effect</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {items.map((item, idx) => (
              <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                <td className="px-6 py-4 font-bold text-red-400">{item.name}</td>
                <td className="px-6 py-4">
                  <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${
                    item.category === 'Magic' ? 'bg-blue-500/10 text-blue-500' :
                    item.category === 'Weapon' ? 'bg-orange-500/10 text-orange-500' :
                    'bg-purple-500/10 text-purple-500'
                  }`}>
                    {item.category}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm text-slate-300">{item.location}</td>
                <td className="px-6 py-4 text-sm text-slate-400 leading-relaxed">{item.effect}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
