using System;
using System.Collections.Generic;
using System.Linq;
using Newtonsoft.Json.Linq;

namespace JuegoDef.Env
{
    /// <summary>
    /// District character pass (owner audit 2026-09-29): the spec fixes the morphology — plots, heights, levels — and
    /// this pass decides what each building IS before it is assembled: a facade family (all render, low base, stone
    /// ground floor, stone, rehabilitated, modern commercial ground floor), its render hue and condition, masonry bond
    /// and tone, quoins, plinth, joinery, roof tiles, and the street's personality (commercial spine, bar street,
    /// river edge, damp residential lanes, calle alta, huerta edge, plaza). Deterministic by plot seed; weights in
    /// one place so a later owner review is a table edit, not new code. Units without a family keep the palette look.
    /// </summary>
    public static class EnvCharacter
    {
        /// <summary>Street personality by street id; rows without a street use their role (river, plaza...).</summary>
        static readonly Dictionary<string, string> StreetKind = new Dictionary<string, string>
        {
            { "Espina_E", "comercial" }, { "Espina_Plaza", "comercial" }, { "Espina_Nodo", "comercial" },
            { "Subida_Puente", "bares" }, { "Cantabra", "bares" }, { "Obispo_Bajo", "bares" }, { "Obispo_Escalera", "bares" },
            { "Ribera", "ribera" }, { "Cervantes", "ribera" }, { "El_Sol", "ribera" }, { "Capitan", "ribera" }, { "Capitan_Salida", "ribera" },
            { "Puente_Piedra", "ribera" },
            { "Calle_Alta_O", "alta" }, { "Calle_Alta_C", "alta" }, { "Calle_Alta_C2", "alta" }, { "Calle_Alta_E", "alta" },
            { "Calle_Alta_Salida", "alta" }, { "San_Pedro", "alta" }, { "San_Pedro_Salida", "alta" },
            { "Ronda_Huertas", "huertas" }, { "Subida_Mirador", "huertas" }, { "Ronda_Mirador", "huertas" },
        };

        // hero lanes (owner reference pass, 2026-09-29): a few lanes carry the everyday life — laundry, pots, chairs,
        // door canopies, slung cables — so they read as lived corners; the rest stay sober by contrast
        public static readonly HashSet<string> HeroStreets = new HashSet<string> { "Cimavilla_Baja", "Fuente", "Fuente_Baja", "Callejon_Arco", "Solana_Bajada" };

        public static string KindOf(JObject row)
        {
            var street = (string)row["street"];
            if (street != null && StreetKind.TryGetValue(street, out var k)) return k;
            var role = (string)row["role"];
            if (role == "river" || role == "bridge" || role == "footbridge") return "ribera";
            if (role == "plaza") return "plaza";
            return "residencial";   // lanes: Callejon_*, Cimavilla, Fuente*, Independencia, Llano, Solana_*
        }

        // family weights per street kind: render, zocalo, stone_ground, stone, rehab, modern
        static readonly Dictionary<string, int[]> FamilyWeights = new Dictionary<string, int[]>
        {
            { "comercial",   new[] { 28, 14, 20, 4, 20, 14 } },
            { "bares",       new[] { 24, 18, 24, 6, 14, 14 } },
            { "plaza",       new[] { 22, 10, 24, 12, 20, 12 } },
            { "ribera",      new[] { 18, 14, 28, 26, 10, 4 } },
            { "residencial", new[] { 30, 24, 20, 12, 14, 0 } },
            { "alta",        new[] { 24, 20, 24, 16, 14, 2 } },
            { "huertas",     new[] { 16, 14, 30, 36, 4, 0 } },
        };
        static readonly string[] Families = { "render", "zocalo", "stone_ground", "stone", "rehab", "modern" };

        static readonly (string, int)[] Hues =
        {
            ("Cal", 18), ("Hueso", 16), ("Crema", 16), ("Ocre", 10), ("Arena", 10), ("Gris", 10), ("Salmon", 6), ("Verdin", 5), ("Anil", 5), ("Tostado", 4),
        };
        static readonly (string, int)[] Bonds = { ("Mamposteria", 40), ("Kit", 20), ("Canto", 15), ("Silleria", 12), ("Laja", 13) };
        static readonly (string, int)[] Tones = { ("Caliza", 30), ("Arenisca", 30), ("Gris", 25), ("Oscura", 15) };
        static readonly (string, int)[] OldJoinery =
        {
            ("ENV_Joinery_Chestnut", 20), ("ENV_Joinery_Walnut", 15), ("ENV_Joinery_Oxblood", 14), ("ENV_Joinery_Green", 12), ("ENV_Joinery_GreenBlue", 9),
            ("ENV_Joinery_Cream", 8), ("ENV_Joinery_Teal", 6), ("ENV_Joinery_Honey", 8), ("ENV_Joinery_Mustard", 3), ("ENV_Joinery_White", 5),
        };
        static readonly (string, int)[] NewJoinery = { ("ENV_Joinery_Bronze", 28), ("ENV_Joinery_Silver", 22), ("ENV_Joinery_PVC", 30), ("ENV_Joinery_Anthracite", 20) };
        static readonly (string, int)[] Roofs =
        {
            ("ENV_Roof_Terracotta", 28), ("ENV_Roof_WetBrown", 14), ("ENV_Roof_TileNew", 9), ("ENV_Roof_TileAged", 26), ("ENV_Roof_TileMossy", 13), ("ENV_Roof_TileDark", 10),
        };
        static readonly string[] Paints = { "ENV_Paint_Plinth_Grey", "ENV_Paint_Plinth_Ochre", "ENV_Paint_Plinth_Oxblood", "ENV_Paint_Plinth_Green" };

        static T Pick<T>(Random rng, (T v, int w)[] table)
        {
            int total = table.Sum(t => t.w), r = rng.Next(total);
            foreach (var (v, w) in table)
            {
                if (r < w) return v;
                r -= w;
            }
            return table[0].v;
        }

        /// <summary>Fills the family fields of <paramref name="bs"/> for a district plot. <paramref name="prevHue"/>
        /// keeps two neighbours from sharing a render colour.</summary>
        public static void Apply(BuildingSpec bs, JObject plot, JObject row, ref string prevHue)
        {
            if ((string)plot["landmark"] == "Torre" || bs.type == "landmark")
            {
                // the tower: dressed ashlar and rubble, aged tiles; its clock, bells and vane come with the landmark type
                bs.family = "stone"; bs.ground = "stone"; bs.upper = "stone"; bs.era = "old"; bs.quoins = "ashlar";
                bs.stone = bs.stoneGround = "ENV_Mason_Silleria_Arenisca"; bs.dressed = "ENV_Dressed_Arenisca";
                bs.render = bs.renderGround = "ENV_Render_Arena_Viejo"; bs.roofMat = "ENV_Roof_TileAged"; bs.joinery = "ENV_Joinery_Walnut";
                return;
            }
            var rng = new Random(bs.seed * 7121 + 3);
            string kind = KindOf(row);
            bool casona = (bool?)plot["casona"] == true;
            bool shop = bs.type == "mixed_commercial";
            var fw = FamilyWeights[kind];
            string family = casona ? "stone" : Families[PickIndex(rng, fw)];
            if (family == "modern" && !shop) family = "rehab";
            bs.family = family;

            string hue = Pick(rng, Hues);
            if (hue == prevHue) hue = Pick(rng, Hues);
            prevHue = hue;
            string bond = casona || (family == "stone" && rng.NextDouble() < 0.3) ? "Silleria" : Pick(rng, Bonds);
            if (kind == "ribera" && rng.NextDouble() < 0.3) bond = "Canto";
            if (kind == "huertas" && rng.NextDouble() < 0.3) bond = "Laja";
            string tone = Pick(rng, Tones);

            // condition and era: rehabilitated and modern fronts are recent; the rest age by a draw, with the damp
            // streets (river, lanes) a little older
            double age = rng.NextDouble() + (kind == "ribera" || kind == "residencial" ? 0.12 : 0) - (kind == "comercial" ? 0.1 : 0);
            string cond = family == "rehab" || family == "modern" ? "Nuevo" : age < 0.3 ? "Nuevo" : age < 0.82 ? "Viejo" : "Gastado";
            bs.era = family == "rehab" || family == "modern" ? "reformed" : cond == "Gastado" ? "neglected" : cond == "Nuevo" && rng.NextDouble() < 0.5 ? "reformed" : "old";
            bs.render = $"ENV_Render_{hue}_{cond}";
            bs.renderGround = $"ENV_Render_{hue}_{cond}_G";
            bs.stone = $"ENV_Mason_{bond}_{tone}";
            bs.stoneGround = $"ENV_Mason_{bond}_{tone}_G";
            bs.dressed = $"ENV_Dressed_{(tone == "Oscura" ? "Oscura" : tone == "Gris" ? "Gris" : tone)}";
            bs.plinthMat = "";
            bs.plinthHeight = 0;
            bs.band = rng.NextDouble() < 0.55 ? bs.render : null;   // many fronts have no floor-line band at all

            switch (family)
            {
                case "render":
                    bs.ground = "plaster"; bs.upper = "plaster";
                    bs.quoins = rng.NextDouble() < 0.72 ? "none" : "painted";
                    if (bs.quoins == "painted") bs.dressed = "ENV_Dressed_Pintada";
                    double pr = rng.NextDouble();
                    if (pr < 0.35) { bs.plinthMat = Paints[rng.Next(Paints.Length)]; bs.plinthHeight = 0.55f + 0.5f * (float)rng.NextDouble(); }
                    else if (pr < 0.5) { bs.plinthMat = bs.dressed == "ENV_Dressed_Pintada" ? "ENV_Dressed_Gris" : bs.dressed; bs.plinthHeight = 0.4f + 0.3f * (float)rng.NextDouble(); }
                    bs.surrounds = rng.NextDouble() < 0.25;
                    if (bs.surrounds && bs.quoins != "painted") bs.dressed = "ENV_Dressed_Pintada";
                    break;
                case "zocalo":
                    bs.ground = "plaster"; bs.upper = "plaster";
                    bs.quoins = rng.NextDouble() < 0.5 ? "none" : "slim";
                    bs.plinthMat = rng.NextDouble() < 0.6 ? bs.stoneGround : bs.dressed;
                    bs.plinthHeight = 0.6f + 0.7f * (float)rng.NextDouble();
                    bs.surrounds = rng.NextDouble() < 0.4;
                    break;
                case "stone_ground":
                    bs.ground = "stone"; bs.upper = "plaster";
                    double q = rng.NextDouble();
                    bs.quoins = q < 0.4 ? "ashlar" : q < 0.75 ? "slim" : "none";
                    bs.surrounds = rng.NextDouble() < 0.45;
                    break;
                case "stone":
                    bs.ground = "stone"; bs.upper = "stone";
                    bs.quoins = casona || rng.NextDouble() < 0.6 ? "ashlar" : "none";
                    bs.surrounds = true;
                    bs.era = "old";
                    bs.band = null;
                    break;
                case "rehab":
                    bs.ground = rng.NextDouble() < 0.35 ? "stone" : "plaster"; bs.upper = "plaster";
                    bs.quoins = rng.NextDouble() < 0.4 ? "slim" : "none";
                    bs.surrounds = rng.NextDouble() < 0.45;
                    if (bs.ground == "plaster" && rng.NextDouble() < 0.5) { bs.plinthMat = bs.dressed; bs.plinthHeight = 0.45f + 0.35f * (float)rng.NextDouble(); }
                    break;
                case "modern":
                    // 1970s-2000s shop conversion: clad ground floor, aluminium shopfront, render above
                    bs.ground = "plaster"; bs.upper = "plaster";
                    bs.renderGround = rng.NextDouble() < 0.6 ? "ENV_Clad_Granite" : "ENV_Clad_Tile";
                    bs.quoins = "none";
                    bs.surrounds = false;
                    break;
            }
            bs.joinery = bs.era == "reformed" ? Pick(rng, NewJoinery) : Pick(rng, OldJoinery);
            bs.roofMat = family == "rehab" && rng.NextDouble() < 0.5 ? "ENV_Roof_TileNew" : Pick(rng, Roofs);
            if ((kind == "ribera" || kind == "residencial") && rng.NextDouble() < 0.25) bs.roofMat = "ENV_Roof_TileMossy";
            bs.pitch = 0.38f + 0.14f * (float)rng.NextDouble();
            // solanas: fewer, and only on old houses (owner: timber + stone read as a medieval set)
            if (bs.solana && (family == "rehab" || family == "modern" || rng.NextDouble() < 0.5)) bs.solana = false;
            // plants belong to damp lanes, old people's doors and the huerta edge, not to every portal
            bs.plantShare = kind == "residencial" ? 0.32f : kind == "huertas" ? 0.3f : kind == "ribera" ? 0.2f : kind == "alta" ? 0.16f : 0.1f;
            bs.hero = HeroStreets.Contains((string)row["street"] ?? "") ? 1f : 0f;
            if (bs.hero > 0) bs.plantShare = Math.Max(bs.plantShare, 0.6f);
            // the ground floor's programme: the business replaces the old random awning / blank bracket sign
            bs.awning = "";
            bs.sign = "";
            if (bs.type == "mixed_commercial") EnvBusiness.Assign(bs, kind);
            else if (bs.type == "lodging") EnvBusiness.AssignLodging(bs);
        }

        static int PickIndex(Random rng, int[] w)
        {
            int total = w.Sum(), r = rng.Next(total);
            for (int i = 0; i < w.Length; i++)
            {
                if (r < w[i]) return i;
                r -= w[i];
            }
            return 0;
        }
    }
}
