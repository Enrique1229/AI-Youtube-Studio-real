import json, subprocess, sys, re, statistics
groups = {
 "SCI-FI EN": "@StarboundHFY @scifistories1977 @HFYZenith @GalacticZenHFY @DystopianHfyStories @BlackCaptainHFY @XSci-fiStories @hfyhunters @HFYVengeance @HFYErythion @GalacticHorrors @VoidOfFears @TheDarkCosmos1 @MagnetarYT",
 "SCI-FI ES": "@CienciayFiccionFHY @HFY_en_Español @HistoriasSci-Fi-es7vf @nebulascifihfy @historia_ciencia_o_ficcion",
 "TERROR ES": "@Relatosdelanoche @RelatosdelLadoOscuro @RELATOSDEHORROR @insomnio.paranormal @Inframundorelatosdeterror @cuentosdelachoza @TerrorEnLaOscuridad @OscuroSecretoRT @ultimohuesped @relatosdeterrordelgato @RelatosdeMiedoar @RelatosdeShell @RelatosdeterrordeSUNO @DomRelatosDeTerror @ElTinteroMaldito @RelatosOscurosHorror",
}
def recent(rows):
    return sum(1 for r in rows if re.search(r"(hour|day|week|minute)s? ago|\d+[hdw] ago|\d+ ?(h|d|w|min)", r["age"]) and "mo" not in r["age"] and "y" not in r["age"].split()[0])
for g, hs in groups.items():
    print(f"\n== {g}  (subs | vídeos totales | subidas últimos ~30 días | mediana vistas | máx | duración mediana | vistas/sub)")
    out = []
    for h in hs.split():
        subprocess.run([sys.executable, "chan.py", h], capture_output=True)
        try: c = json.load(open(f"ch_{h.strip('@')}.json"))
        except Exception: print("   fallo", h); continue
        from yt import num
        s = num(c["subs"] or "0") or 0; rows = c["rows"]
        live = [r for r in rows if r["views"]]
        med = int(statistics.median([r["views"] for r in live])) if live else 0
        out.append((med, f"{c['title'][:30]:30} | {c['subs'] or '?':>6} | {c['videos'] or '?':>5} | {recent(rows):>2}{'+' if recent(rows) >= 30 else ' '} | {med:>8} | {c['max_views'] or 0:>8} | {c['median_min'] or 0:>5} min | {med / s:.2f}" if s else c['title']))
    for _, l in sorted(out, reverse=True): print("  ", l)
