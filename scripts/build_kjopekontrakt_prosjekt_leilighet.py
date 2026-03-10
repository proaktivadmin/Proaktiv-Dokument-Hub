"""
Build script: Kjøpekontrakt prosjekt (leilighet / eierseksjon under oppføring)
Source: 8966142_3.htm
Output: scripts/converted_html/Kjopekontrakt_prosjekt_leilighet_PRODUCTION.html
"""

import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "converted_html")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "Kjopekontrakt_prosjekt_leilighet_PRODUCTION.html")

TEMPLATE = """\
<div class="proaktiv-theme" id="vitecTemplate">
<span vitec-template="resource:Vitec Stilark">&nbsp;</span>
<style type="text/css">
#vitecTemplate { counter-reset: section; }
#vitecTemplate article.item:not(article.item article.item) {
  counter-increment: section;
  counter-reset: subsection;
}
#vitecTemplate article.item article.item { counter-increment: subsection; }
#vitecTemplate article.item:not(article.item article.item) > h2::before {
  content: counter(section) ". ";
}
#vitecTemplate article.item article.item > h3::before {
  content: counter(section) "." counter(subsection) ". ";
}
#vitecTemplate article { padding-left: 20px; }
#vitecTemplate article article { padding-left: 0; }
#vitecTemplate .avoid-page-break { page-break-inside: avoid; }
#vitecTemplate .roles-table { width: 100%; table-layout: fixed; border-collapse: collapse; }
#vitecTemplate .roles-table th { text-align: left; padding: 4px 6px; border-bottom: 1px solid #000; }
#vitecTemplate .roles-table td { padding: 4px 6px; vertical-align: top; }
#vitecTemplate .roles-table tbody:last-child tr:last-child td { display: none; }
#vitecTemplate .costs-table { width: 100%; table-layout: fixed; border-collapse: collapse; }
#vitecTemplate .costs-table td { padding: 2px 6px; vertical-align: top; }
#vitecTemplate .costs-table tr.sum-row td { border-top: 1px solid #000; font-weight: bold; }
#vitecTemplate .insert { border-bottom: 1px dotted #999; min-width: 80px; display: inline-block; }
</style>

<p>Oppdragsnummer: [[oppdrag.nr]]<br>
Omsetningsnummer: [[kontrakt.formidling.nr]]</p>

<h5 style="text-align:center;">KJØPEKONTRAKT</h5>
<p style="text-align:center;">om rett til bolig eller fritidsbolig under oppføring med tomt</p>

<p>Kontraktens bestemmelser utfylles av bustadoppføringslova (bustadoppføringslova) av 13. juni nr. 43 1997 og annen bakgrunnsrett. Kontrakten gjelder avtale etter lovens § 1, første ledd b), avtale om bolig eller fritidsbolig under oppføring og hvor avtalen også omfatter rett til grunn.</p>

<p>Mellom &ldquo;selger&rdquo;</p>

<table class="roles-table" vitec-if="Model.selgere.Count &gt; 0">
<thead>
<tr>
  <th colspan="34"><strong>Navn</strong></th>
  <th colspan="48"><strong>Adresse</strong></th>
  <th colspan="18"><strong>[[selger.ledetekst_fdato_orgnr]]</strong></th>
</tr>
</thead>
<tbody vitec-foreach="selger in Model.selgere">
<tr>
  <td colspan="34">[[*selger.navnutenfullmektigogkontaktperson]]</td>
  <td colspan="48">[[*selger.gatenavnognr]], [[*selger.postnr]] [[*selger.poststed]]</td>
  <td colspan="18">[[*selger.fdato_orgnr]]</td>
</tr>
<tr>
  <td colspan="100">
    <span vitec-if="selger.tlf != &quot;&quot;">Mob: [[*selger.tlf]]</span>
    <span vitec-if="(selger.tlf != &quot;&quot; &amp;&amp; selger.emailadresse != &quot;&quot;)"> / </span>
    <span vitec-if="selger.emailadresse != &quot;&quot;">E-post: [[*selger.emailadresse]]</span>
  </td>
</tr>
<tr><td colspan="100">&nbsp;</td></tr>
</tbody>
</table>

<p>Gyldig legitimasjon: <span class="insert">&nbsp;</span></p>

<p vitec-if="Model.selger.fullmektig.navn != &quot;&quot;">Selger er representert ved fullmektig [[selger.fullmektig.navn]], som også har fremvist gyldig legitimasjon: <span class="insert">&nbsp;</span></p>

<p>og &ldquo;kjøper&rdquo;</p>

<table class="roles-table" vitec-if="Model.kjopere.Count &gt; 0">
<thead>
<tr>
  <th colspan="34"><strong>Navn</strong></th>
  <th colspan="48"><strong>Adresse</strong></th>
  <th colspan="18"><strong>[[kjoper.ledetekst_fdato_orgnr]]</strong></th>
</tr>
</thead>
<tbody vitec-foreach="kjoper in Model.kjopere">
<tr>
  <td colspan="34">[[*kjoper.navnutenfullmektigogkontaktperson]]</td>
  <td colspan="48">[[*kjoper.gatenavnognr]], [[*kjoper.postnr]] [[*kjoper.poststed]]</td>
  <td colspan="18">[[*kjoper.fdato_orgnr]]</td>
</tr>
<tr>
  <td colspan="100">
    <span vitec-if="kjoper.tlf != &quot;&quot;">Mob: [[*kjoper.tlf]]</span>
    <span vitec-if="(kjoper.tlf != &quot;&quot; &amp;&amp; kjoper.emailadresse != &quot;&quot;)"> / </span>
    <span vitec-if="kjoper.emailadresse != &quot;&quot;">E-post: [[*kjoper.emailadresse]]</span>
  </td>
</tr>
<tr><td colspan="100">&nbsp;</td></tr>
</tbody>
</table>

<p>Gyldig legitimasjon, kjøpere: <span class="insert">&nbsp;</span></p>

<p>er i dag inngått følgende kjøpekontrakt:</p>

<!-- ===== SECTION 1A: Selveiet bolig ===== -->
<div vitec-if="Model.eiendom.eieform != &quot;Eierseksjon&quot;">
<article class="item">
<h2>SALGSOBJEKT OG TILBEHØR</h2>
<p style="text-align:center;">(selveiet bolig/fritidsbolig)</p>

<p>Kontrakten gjelder kjøp av</p>

<p>
  <span vitec-if="Model.eiendom.grunntype == &quot;Bolig&quot;">&#9745;</span>
  <span vitec-if="Model.eiendom.grunntype != &quot;Bolig&quot;">&#9744;</span>
  bolig
</p>
<p>
  <span vitec-if="Model.eiendom.grunntype == &quot;Fritid&quot;">&#9745;</span>
  <span vitec-if="Model.eiendom.grunntype != &quot;Fritid&quot;">&#9744;</span>
  fritidsbolig
</p>

<p>på fradelt tomt fra/med gårdsnr. <span class="insert">&nbsp;</span> bruksnr. <span class="insert">&nbsp;</span> i [[eiendom.kommunenavn]] kommune.</p>

<p>Tomten er:</p>
<p>
  <span vitec-if="Model.eiendom.tomtetype == &quot;eiertomt&quot;">&#9745;</span>
  <span vitec-if="Model.eiendom.tomtetype != &quot;eiertomt&quot;">&#9744;</span>
  eiet
</p>
<p>
  <span vitec-if="Model.eiendom.tomtetype == &quot;festetomt&quot;">&#9745;</span>
  <span vitec-if="Model.eiendom.tomtetype != &quot;festetomt&quot;">&#9744;</span>
  festet
</p>

<p><span vitec-if="Model.eiendom.grunntype == &quot;Bolig&quot;">Boligen</span><span vitec-if="Model.eiendom.grunntype == &quot;Fritid&quot;">Fritidsboligen</span> leveres som angitt i kravspesifikasjoner, tegninger, prospekt mv. som kjøper er kjent med og som følger som vedlegg til denne kontrakt.</p>

<p>Selger kan foreta nødvendige og/eller hensiktsmessige endringer i spesifikasjonene, f.eks. som følge av offentligrettslige krav, manglende tilgjengelighet eller prisendringer, så lenge dette ikke reduserer <span vitec-if="Model.eiendom.grunntype == &quot;Bolig&quot;">boligens</span><span vitec-if="Model.eiendom.grunntype == &quot;Fritid&quot;">fritidsboligens</span> forutsatte standard. Dette gjelder også for endringer/tilvalg. Slike endringer utgjør ikke en mangel, og gir ikke kjøper rett til prisavslag eller andre sanksjoner.</p>

<p>Tegninger og illustrasjoner i prospektet og tegningsmaterialet er kun av illustrativ karakter. Ved eventuelle avvik gjelder leveransebeskrivelsen foran prospektet og tegninger.</p>
</article>
</div>

<!-- ===== SECTION 1B: Eierseksjon/sameie ===== -->
<div vitec-if="Model.eiendom.eieform == &quot;Eierseksjon&quot;">
<article class="item">
<h2>SALGSOBJEKT OG TILBEHØR</h2>
<p style="text-align:center;">(bolig/fritidsbolig i sameie)</p>

<p>Kontrakten gjelder kjøp av</p>

<p>
  <span vitec-if="Model.eiendom.grunntype == &quot;Bolig&quot;">&#9745;</span>
  <span vitec-if="Model.eiendom.grunntype != &quot;Bolig&quot;">&#9744;</span>
  bolig i eierseksjonssameie
</p>
<p>
  <span vitec-if="Model.eiendom.grunntype == &quot;Fritid&quot;">&#9745;</span>
  <span vitec-if="Model.eiendom.grunntype != &quot;Fritid&quot;">&#9744;</span>
  fritidsbolig i eierseksjonssameie
</p>

<p>på fradelt tomt fra/med gårdsnr. <span class="insert">&nbsp;</span> bruksnr. <span class="insert">&nbsp;</span> i [[eiendom.kommunenavn]] kommune.</p>

<p>Tomten er:</p>
<p>
  <span vitec-if="Model.eiendom.tomtetype == &quot;eiertomt&quot;">&#9745;</span>
  <span vitec-if="Model.eiendom.tomtetype != &quot;eiertomt&quot;">&#9744;</span>
  eiet
</p>
<p>
  <span vitec-if="Model.eiendom.tomtetype == &quot;festetomt&quot;">&#9745;</span>
  <span vitec-if="Model.eiendom.tomtetype != &quot;festetomt&quot;">&#9744;</span>
  festet
</p>

<p>Selger besørger og bekoster seksjonering. Seksjonens endelige seksjonsnummer vil bli tildelt når seksjonering er gjennomført, senest innen overtagelse. Dersom boligen overleveres før eiendommen er seksjonert, gjøres kjøper oppmerksom på at ved evt. utleie risikerer kjøper krav fra leietakerne om å overta seksjonen til 80% av markedsverdi jfr. Eierseksjonsloven.</p>

<p><span vitec-if="Model.eiendom.grunntype == &quot;Bolig&quot;">Boligen</span><span vitec-if="Model.eiendom.grunntype == &quot;Fritid&quot;">Fritidsboligen</span> er foreløpig betegnet som leilighet nr. [[eiendom.leilighetsnr]].</p>

<p>Til boligen/fritidsboligen medfølger:</p>
<p>&#9744; Garasjeplass(er), antall <span class="insert">&nbsp;</span></p>
<p>&#9744; Parkeringsplass(er), antall <span class="insert">&nbsp;</span></p>
<p>&#9744; Bruksrett til del av fellesarealer, se vedlegg</p>
<p>&#9744; Tilleggsareal, se vedlegg</p>
<p>&#9744; Gjesteparkering, antall plasser <span class="insert">&nbsp;</span>, felles for sameiet, se vedlegg</p>

<p>Hjemmelshaver til eiendommen er</p>
<p>1) selger(e) <span class="insert">&nbsp;</span></p>
<p>2) annen: navn <span class="insert">&nbsp;</span> fødsels- eller foretaksnr. <span class="insert">&nbsp;</span></p>

<p>Prosjektet er planlagt med [[oppdrag.prosjekt.antallenheter]] enheter.</p>

<p>Boligene/fritidsboligene leveres som angitt i kravspesifikasjoner, tegninger, prospekt mv. som kjøper er kjent med og som følger som vedlegg til denne kontrakt.</p>

<p>Selger kan foreta nødvendige og/eller hensiktsmessige endringer i spesifikasjonene, f.eks. som følge av offentligrettslige krav, manglende tilgjengelighet eller prisendringer, så lenge dette ikke reduserer boligens/fritidsboligens forutsatte standard. Dette gjelder også for endringer/tilvalg. Slike endringer utgjør ikke en mangel, og gir ikke kjøper rett til prisavslag eller andre sanksjoner.</p>

<p>Tegninger og illustrasjoner i prospektet og tegningsmaterialet er kun av illustrativ karakter. Ved eventuelle avvik gjelder leveransebeskrivelsen foran prospektet og tegninger.</p>

<p>Kjøper er kjent med at det med boligen/fritidsboligen medfølger et ansvar for å dekke eiendommens andel av de månedlige felleskostnadene. Seksjonens månedlige felleskostnader er ut fra blant annet erfaringstall stipulert til kr. [[eiendom.fellesutgifter]] for første driftsår. Kjøper er kjent med at felleskostnadene kan bli justert etter endringer i konsumprisindeks, vedlikeholdsbehov, sameiets egne vedtak mm. Det tas forbehold om at Selger kan justere felleskostnadene som følge av endringer i budsjettpostene.</p>
</article>
</div>

<!-- ===== SECTION 2 ===== -->
<article class="item">
<h2>KJØPESUM OG OMKOSTNINGER</h2>

<p>Eiendommen overdras for en kjøpesum</p>

<p><u>kr $.UD([[kontrakt.kjopesum]]) &ndash; [[kontrakt.kjopesumibokstaver]], 00/100</u>, heretter kalt &ldquo;kjøpesummen&rdquo;</p>

<p>som gjøres opp på følgende måte:</p>

<table class="costs-table">
<tbody>
<tr>
  <td colspan="60">Vederlag for tomten innen overtakelsen av tomten</td>
  <td colspan="30" style="text-align:right;">kroner</td>
  <td colspan="10" style="text-align:right;"><span class="insert">&nbsp;</span></td>
</tr>
<tr>
  <td colspan="60">Delbetaling ved (angi forfallstidspunkt)</td>
  <td colspan="30" style="text-align:right;">kroner</td>
  <td colspan="10" style="text-align:right;"><span class="insert">&nbsp;</span></td>
</tr>
<tr>
  <td colspan="60">Delbetaling ved (angi forfallstidspunkt)</td>
  <td colspan="30" style="text-align:right;">kroner</td>
  <td colspan="10" style="text-align:right;"><span class="insert">&nbsp;</span></td>
</tr>
<tr>
  <td colspan="60">Rest kjøpesum før overtakelse (min 10%)</td>
  <td colspan="30" style="text-align:right;">kroner</td>
  <td colspan="10" style="text-align:right;"><span class="insert">&nbsp;</span></td>
</tr>
<tr class="sum-row">
  <td colspan="60"><u>Kjøpesum</u></td>
  <td colspan="30" style="text-align:right;"><u>kroner</u></td>
  <td colspan="10" style="text-align:right;"><u>$.UD([[kontrakt.kjopesum]])</u></td>
</tr>
</tbody>
</table>

<p>I tillegg til kjøpesummen må kjøper betale følgende omkostninger:</p>

<table class="costs-table">
<tbody>
<tr>
  <td colspan="70">Dokumentavgift til Staten, 2,5 % av tomteverdien</td>
  <td colspan="15" style="text-align:right;">kr</td>
  <td colspan="15" style="text-align:right;"><span class="insert">&nbsp;</span>,-</td>
</tr>
<tr>
  <td colspan="70">Tinglysingsgebyr for skjøte</td>
  <td colspan="15" style="text-align:right;">kr</td>
  <td colspan="15" style="text-align:right;"><span class="insert">&nbsp;</span>,-</td>
</tr>
<tr>
  <td colspan="70">Tinglysingsgebyr for pantedokument</td>
  <td colspan="15" style="text-align:right;">kr</td>
  <td colspan="15" style="text-align:right;"><span class="insert">&nbsp;</span>,-</td>
</tr>
<tr>
  <td colspan="70">Attestgebyr</td>
  <td colspan="15" style="text-align:right;">kr</td>
  <td colspan="15" style="text-align:right;"><span class="insert">&nbsp;</span>,-</td>
</tr>
<tr>
  <td colspan="70">I tillegg skal kjøper innbetale forskudd til driftskonto</td>
  <td colspan="15" style="text-align:right;">kr</td>
  <td colspan="15" style="text-align:right;"><span class="insert">&nbsp;</span>,-</td>
</tr>
<tr class="sum-row">
  <td colspan="70"><u>Sum omkostninger</u></td>
  <td colspan="15" style="text-align:right;"><u>Kr</u></td>
  <td colspan="15" style="text-align:right;"><u>[[kontrakt.totaleomkostninger]],-</u></td>
</tr>
</tbody>
</table>

<table class="costs-table">
<tbody>
<tr class="sum-row">
  <td colspan="70"><u>Kjøpesum inkl. omkostninger, i alt</u></td>
  <td colspan="15" style="text-align:right;"><u>Kr</u></td>
  <td colspan="15" style="text-align:right;"><u>[[kontrakt.kjopesumogomkostn]],-</u></td>
</tr>
</tbody>
</table>

<p>Det tas forbehold om endringer i offentlige avgifter/gebyrer.</p>
</article>

<!-- ===== SECTION 3 ===== -->
<article class="item">
<h2>SELGERS PLIKT TIL Å STILLE GARANTIER</h2>

<p>Selger skal, umiddelbart etter at avtale er inngått, stille garanti etter bustadoppføringslova § 12. Garantien skal gjelde fra tidspunkt for avtaleinngåelse og frem til fem år etter overtagelse. Garantien skal tilsvare minst 3 % av kjøpesummen frem til overtagelse, og minst 5 % etter overtagelse.</p>
</article>

<!-- ===== SECTION 4 ===== -->
<article class="item">
<h2>OPPGJØR</h2>

<p>Oppgjøret mellom partene foretas av megler og gjennomføres i henhold til inngått avtale mellom kjøper og selger.</p>

<p>Oppgjøret mellom partene foretas av meglerforetakets oppgjørsavdeling:</p>

<table style="width:100%; table-layout:fixed;">
<tbody>
<tr><td colspan="100">[[oppgjor.kontornavn]]</td></tr>
<tr><td colspan="100">[[oppgjor.besoksadresse]], [[oppgjor.besokspostnr]] [[oppgjor.besokspoststed]]</td></tr>
<tr>
  <td colspan="50">Tlf: [[oppgjor.kontortlf]]</td>
  <td colspan="50">E-post: [[oppgjor.kontorepost]]</td>
</tr>
</tbody>
</table>

<p>Dette endrer ikke ansvarsforholdet som meglerforetaket har overfor kjøper og selger.</p>

<p>Det er avtalt følgende oppgjørsform:</p>

<p>&#9744; For tomten: Kjøper betaler vederlaget for tomt som beskrevet i punkt 2 snarest mulig etter avtaleinngåelsen, hvoretter eiendomsretten til tomten går over til kjøper. Rådigheten til vederlaget for tomten går over til selger så snart tomten er tinglyst i kjøpers navn, uten andre heftelser enn de som eventuelt er avtalt å følge med.</p>

<p>&#9744; For boligen: Kjøper betaler ingen del av kjøpesummen for boligen før skjøtet for tomten er tinglyst, i avtalt stand. Når skjøtet er tinglyst i avtalt stand, betaler kjøper for boligen i som beskrevet i punkt 2 etter hvert som bygget skrider frem. Verdiene som er tilført kjøpers tomt skal tilsvare betalingene fra kjøper. Minst 10 % av vederlaget (&ldquo;Restkjøpesummen&rdquo;) skal gjenstå å betale ved overtagelse av boligen. Restkjøpesummen skal være innbetalt til megler senest samtidig med overtagelsen.</p>

<p>Selger skal besørge og bekoste at en uavhengig og kompetent fagperson, i forkant av hver betaling fra kjøper, skal befare eiendommen og forelegges nødvendig informasjon for å kunne verifisere at verdiene som blir tilført kjøpers tomt tilsvarer betalingene fra kjøper.</p>

<p>Kjøper har ingen plikt til å innbetale noen del av kjøpesummen, verken for tomt eller bolig før entreprenørgaranti etter bustadoppføringslova § 12 er stilt.</p>

<p>Alle innbetalinger (total kjøpesum inkl. omkostninger) skal være kreditert eiendomsmeglers klientkonto <strong>[[kontrakt.klientkonto]]</strong> og merkes med <strong>[[kontrakt.kid]]</strong>.</p>

<p>Ved omtvistet beløp har kjøper deponeringsrett i henhold til bustadoppføringslovens § 49.</p>

<p>Fordeling av eiendommens driftsutgifter og eventuelle inntekter pr. overtagelsesdato settes opp av kjøper og selger. Ønsker partene eiendomsmeglers bistand til dette, inngås det særskilt avtale om det.</p>

<p>Rentene av innestående på klientkonto tilfaller som hovedregel kjøper.</p>

<p>Når selger har oppfylt vilkårene om å stille garanti etter bustadoppføringslova § 12 og kjøper har fått heftelsesfri hjemmel til tomten, godskrives derfor selger renter av innestående på klientkonto til enhver tid. Renter av omkostninger som er innbetalt av kjøper tilfaller kjøper. Kjøper og selger godskrives likevel ikke renter når disse for hver av partene utgjør mindre enn et halvt rettsgebyr, jf. eiendomsmeglingsforskriften § 3-10 (3).</p>
</article>

<!-- ===== SECTION 5 ===== -->
<article class="item">
<h2>HEFTELSER</h2>

<p>Utskrift av eiendommens grunnbok er forelagt kjøper. Kjøper har gjort seg kjent med innholdet i denne.</p>

<p><strong>Pengeheftelser:</strong></p>

<p>
  <span vitec-if="Model.eiendom.heftelserogrettigheter == &quot;&quot;">&#9745;</span>
  <span vitec-if="Model.eiendom.heftelserogrettigheter != &quot;&quot;">&#9744;</span>
  Eiendommen overdras fri for pengeheftelser.
</p>

<p>
  <span vitec-if="Model.eiendom.heftelserogrettigheter != &quot;&quot;">&#9745;</span>
  <span vitec-if="Model.eiendom.heftelserogrettigheter == &quot;&quot;">&#9744;</span>
  Eiendommen overdras fri for pengeheftelser, med unntak for følgende dokumenter:
</p>
<p vitec-if="Model.eiendom.heftelserogrettigheter != &quot;&quot;">[[eiendom.heftelserogrettigheter]]</p>

<p>Pengeheftelser som ikke skal følge med eiendommen, skal slettes for selgers regning.</p>

<p>Selger opplyser at det ikke eksisterer pengeheftelser av noen art, herunder utleggsforretninger, utover det som grunnboksutskriften viser. Selger forplikter seg til umiddelbart å underrette megler dersom slike forretninger blir avholdt innen tinglysing av skjøtet skal finne sted. Videre forplikter selger seg til å betale alle avgifter m.v. som vedrører eiendommen og som er forfalt eller forfaller før overtagelsen.</p>

<p>Selger gir herved megler ugjenkallelig fullmakt til å innfri pengeheftelser som fremgår av bekreftet grunnboksutskrift/oppgjørsskjema og som det ikke er avtalt at kjøper skal overta, og evt. ubetalte avgifter mv. som nevnt over.</p>

<p><strong>Andre heftelser:</strong></p>

<p>&#9744; Det er ikke tinglyst andre heftelser på eiendommen.</p>

<p>&#9744; Følgende andre heftelser er tinglyst på eiendommen, og skal følge med ved salget:</p>
<p><span class="insert">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span></p>

<p>Selger har rett til å tinglyse nye heftelser på eiendommen som følge av krav fra det offentlige, herunder heftelser som gjelder vei, vann og avløp.</p>
</article>

<!-- ===== SECTION 6 ===== -->
<article class="item">
<h2>TINGLYSING/SIKKERHET</h2>

<p>Selger utsteder skjøte til kjøper samtidig med denne kontrakts underskrift. Skjøtet skal oppbevares hos eiendomsmegler, som foretar tinglysing når kjøper har innbetalt vederlaget for tomten i henhold til punkt 2, inklusive omkostninger. Partene gir meglerforetaket fullmakt til å påføre rett matrikkel på skjøte når dette foreligger.</p>

<p>Selger har utstedt et pantedokument (sikringspantedokument) til megler som lyder på et beløp minst tilsvarende kjøpesummen. Pantedokumentet inneholder også en urådighetserklæring. Pantedokumentet er tinglyst, eller skal tinglyses, av eiendomsmegler. Pantedokumentet tjener som sikkerhet for den til enhver tid utbetalte del av salgssummen.</p>

<p>Eiendomsmegleren skal vederlagsfritt besørge pantedokumentet slettet når oppgjør mellom partene er avsluttet og skjøtet er godtatt til tinglysning.</p>

<p>All tinglysing av dokumenter på eiendommen skal foretas av eiendomsmegler. Dokumenter som skal tinglyses må snarest, og i god tid før overtakelse, overleveres eiendomsmegler i undertegnet og tinglysingsklar stand.</p>
</article>

<!-- ===== SECTION 7 ===== -->
<article class="item">
<h2>SELGERS MANGELSANSVAR/KJØPERS REKLAMASJONSSPLIKT</h2>

<p>Det foreligger mangel ved avvik fra avtalt ytelse eller avvik fra offentligrettslige krav som beskrevet i bustadoppføringslova § 25, ved manglende opplysninger som beskrevet i § 26 eller ved uriktige opplysninger som beskrevet i § 27.</p>

<p>Foreligger det mangel, kan kjøper gjøre gjeldende slike krav som følger av bustadoppføringslova §§ 29 flg., herunder retting av mangel, tilbakeholdel av kjøpesum, erstatning eller heving, på nærmere vilkår som beskrevet i bustadoppføringslova.</p>

<p>Kjøperen mister retten til å gjøre mangler gjeldende dersom det ikke rettidig er sendt reklamasjon til selger i tråd med bustadoppføringslova § 30.</p>

<p>Selger er ikke ansvarlig for mangler, skjulte eller åpenbare, som skyldes kjøperens bruk av eiendommen eller krymping av materialer og derav sprekker i tapet, maling eller lignende.</p>
</article>

<!-- ===== SECTION 8 ===== -->
<article class="item">
<h2>ENDRINGSARBEIDER, TILLEGGSARBEIDER OG TILVALG</h2>

<p>Kjøper kan kreve endringer, og partene kan kreve justering av vederlaget, i henhold til bustadoppføringslovas regler. Partene har avtalt at kjøperen ikke kan kreve endringer som vil endre kjøpesummen med 15 prosent eller mer.</p>

<p>Partene er enige om at alle endringer, tillegg eller tilvalg (kalt &ldquo;Endringer&rdquo; som fellesbetegnelse) til kontrakten skal skje skriftlig og med kopi til megler, også etter inngåelsen av kjøpekontrakten.</p>

<p>Endringene blir en del av kjøpekontrakten, på samme måte som de opprinnelig avtalte hovedytelsene: Endringene innebærer at beskrivelsen av salgsobjektet i punkt 1, med vedlegg, justeres i henhold til de avtalte endringer og tilvalg. Det er også etter Endringene selger som er ansvarlig for hele leveransen av boligen/fritidsboligen, og kjøper kan forholde seg til selger ved eventuell forsinkelse eller mangler knyttet til Endringene. Kjøper er ansvarlig for å betale hele kjøpesummen, inkludert betaling for Endringene, til meglers klientkonto. Selgers forpliktelse til å stille garantier etter denne kontrakten og bustadoppføringslova § 47 vil gjelde tilsvarende for Endringene.</p>
</article>

<!-- ===== SECTION 9 ===== -->
<article class="item">
<h2>OVERTAKELSE</h2>

<div vitec-if="Model.kontrakt.overtagelse.dato != &quot;Mangler data&quot;">
<p>&#9745; Eiendommen overtas av kjøper den <strong>[[kontrakt.overtagelse.dato]]</strong> med alle rettigheter og forpliktelser slik den har tilhørt selger, forutsatt at kjøper har oppfylt sine forpliktelser.</p>
<p>&#9744; Forventet ferdigstillelse er <span class="insert">&nbsp;</span>, men dette tidspunktet er foreløpig og ikke bindende og utløser ikke dagmulkt.</p>
</div>

<div vitec-if="Model.kontrakt.overtagelse.dato == &quot;Mangler data&quot;">
<p>&#9744; Eiendommen overtas av kjøper den <span class="insert">&nbsp;</span> med alle rettigheter og forpliktelser slik den har tilhørt selger, forutsatt at kjøper har oppfylt sine forpliktelser.</p>
<p>&#9745; Forventet ferdigstillelse er <span class="insert">&nbsp;</span>, men dette tidspunktet er foreløpig og ikke bindende og utløser ikke dagmulkt.</p>
</div>

<p>Når selger har opphevet forbeholdene stilt i avtalen skal selger fastsette en overtakelsesperiode som ikke skal være lenger enn 3 måneder. Selger skal skriftlig varsle kjøper om når overtakelsesperioden begynner og slutter. Senest 10 uker før ferdigstillelse av boligen skal selger gi kjøper skriftlig melding om endelig overtakelsesdato. Den endelige datoen er bindende og dagmulktsutløsende, og skal ligge innenfor overtakelsesperioden.</p>

<p>Selger skal innkalle til overtakelsesforretning etter bustadoppføringslova § 15. Selger er ansvarlig for at det skrives protokoll fra overtakelsesforretningen, i henhold til bilag til denne kontrakt.</p>

<p>Kjøper svarer fra overtagelsen for alle eiendommens utgifter og oppebærer eventuelle inntekter.</p>

<p>Selger skal overlevere eiendommen til kjøper i ryddig og byggrengjort stand, uten leieforhold av noen art, slik at hele eiendommen leveres ledig for kjøper. Eiendommen skal ha ferdigattest eller midlertidig brukstillatelse før overlevering til kjøper.</p>

<p>Kjøper gjøres oppmerksom på at fellesarealene overtas samtidig med boligen på overtakelsesdagen. Dersom det er mangler ved fellesarealene på overtakelsestidspunktet, og kjøper ønsker å tilbakeholde et beløp etter bustadoppføringslovas § 31 for å sikre retting/ferdigstillelse, skal dette protokollføres på overtakelsesprotokollen eller på annen måte skriftlig varsles eiendomsmegler og selger før hjemmelsovergang.</p>

<p>På et senere tidspunkt enn overtakelse kan selger innkalle styret i sameiet for kontrollbefaring av fellesarealene. Kjøperne skal i så tilfelle orienteres om utfallet av kontrollbefaringen. Styrets eventuelle konklusjoner vil kun være veiledende for kjøperne og gir ikke styret anledning til å frigi kjøpernes eventuelle tilbakeholdte beløp, uten at kjøper skriftlig samtykker til det.</p>

<p>Ved overtakelse mot midlertidig brukstillatelse, for eksempel der fellesarealene ikke er ferdigstilt, er selger forpliktet til å fremskaffe ferdigattest innen rimelig tid og senest før midlertidig brukstillatelse er utløpt på tid. Skulle denne situasjonen oppstå, er megler forpliktet etter eiendomsmeglingsloven til å gjøre kjøper oppmerksom på at det bør etableres tilstrekkelig sikkerhet for kjøpers krav. Megler skal deretter bistå partene med å etablere et tilfredsstillende sikkerhetsarrangement som ivaretar kjøpers interesser.</p>

<p>Risikoen for eiendommen går over på kjøper når kjøper har overtatt bruken av eiendommen. Overtar kjøper ikke til fastsatt tid, og årsaken ligger hos ham, har kjøper risikoen fra det tidspunktet eiendommen kunne vært overtatt.</p>

<p>Når risikoen for eiendommen er gått over på kjøper, faller ikke kjøpers plikt til å betale kjøpesummen bort ved at eiendommen blir ødelagt eller skadet som følge av en hendelse som selger ikke svarer for.</p>

<p>Dersom ikke annet er avtalt, utleveres nøklene til eiendommen ved overtagelsesbefaringen såfremt kjøpesum og omkostninger er bekreftet innbetalt. Dersom selger utleverer nøkler til kjøper før innbetaling som ovenfor nevnt er bekreftet, bærer selger selv risikoen og oppdragsansvarlig er uten ansvar for dette.</p>
</article>

<!-- ===== SECTION 10 ===== -->
<article class="item">
<h2>ETTÅRSBEFARING</h2>

<p>Selger skal med rimelig frist sørge for at det skriftlig innkalles til ettårsbefaring når det er gått om lag ett år siden overtakelsen, jf. bustadoppføringslova § 16.</p>
</article>

<!-- ===== SECTION 11 ===== -->
<article class="item">
<h2>SELGERS KONTRAKTSBRUDD</h2>

<p>Er selgers ytelse forsinket etter kjøpekontraktens bestemmelser sammenholdt med bustadoppføringslova § 17, kan kjøper kreve sanksjoner som nærmere beskrevet i bustadoppføringslova §§ 18 flg. Slike sanksjoner kan være å holde igjen hele eller deler av kjøpesummen, kreve dagmulkt, kreve erstatning eller å heve avtalen, på nærmere vilkår i bustadoppføringslova.</p>
</article>

<!-- ===== SECTION 12 ===== -->
<article class="item">
<h2>KJØPERS KONTRAKTSBRUDD</h2>

<p>Er kjøpers betaling eller annen medvirkning ikke oppfylt til avtalt tid eller til tidspunkt selger kan kreve etter bustadoppføringslova §§ 46, 47, 50 og 51 kan selger kreve sanksjoner som nærmere beskrevet i bustadoppføringslova §§ 56 flg. Slike sanksjoner kan være å stanse arbeidet og kreve tilleggsvederlag, kreve rente og erstatning for rentetap eller heve avtalen og kreve erstatning for tap, på nærmere vilkår i bustadoppføringslova.</p>

<p>Selger tar forbehold om å heve kontrakten ved kjøpers vesentlige mislighold, selv om kjøper har overtatt bruken av boligen/fritidsboligen og/eller skjøtet er tinglyst før kjøper har oppfylt sine forpliktelser etter kjøpekontrakten.</p>

<p>Blir avtalen hevet som følge av manglende oppfyllelse fra kjøper etter overtagelse, vedtar kjøper tvangsfravikelse i tråd med tvangsfullbyrdelsesloven § 13-2.</p>
</article>

<!-- ===== SECTION 13 ===== -->
<article class="item">
<h2>FORSIKRING</h2>

<p>Eiendommen er fullverdiforsikret i <span class="insert">&nbsp;</span></p>

<p>Selger er forpliktet til å holde eiendommen fullverdiforsikret frem til overtakelsesdagen. Ved overtakelse går forsikringsplikten over på kjøper, eller på sameiet ved kjøp av eierseksjon.</p>

<p>Dersom eiendommen før overtakelse blir utsatt for skade ved brann eller andre forhold som dekkes av forsikringen, har kjøper rett til å tre inn i forsikringsavtalen.</p>

<p>Evt. innboforsikring må betales av kjøper fra overtakelse.</p>
</article>

<!-- ===== SECTION 14 ===== -->
<article class="item">
<h2>AVBESTILLING</h2>

<p>Kjøper kan avbestille i henhold til reglene i bustadoppføringslova §§ 52 og 53. Slik avbestilling kan gi selger rett til økonomisk kompensasjon.</p>
</article>

<!-- ===== SECTION 15 ===== -->
<article class="item">
<h2>SELGERS FORBEHOLD</h2>

<p>Selger tar følgende forbehold for gjennomføring av kontrakten:</p>

<p vitec-if="Model.oppdrag.prosjekt.erutbyggersforbeholdsalgsgrad == true">&#9745; <span class="insert">&nbsp;</span> % av boligene er solgt</p>
<p vitec-if="Model.oppdrag.prosjekt.erutbyggersforbeholdsalgsgrad != true">&#9744; <span class="insert">&nbsp;</span> % av boligene er solgt</p>

<p vitec-if="Model.oppdrag.prosjekt.erutbyggersforbeholdigangsettelse == true">&#9745; kommunen gir igangsettelsestillatelse</p>
<p vitec-if="Model.oppdrag.prosjekt.erutbyggersforbeholdigangsettelse != true">&#9744; kommunen gir igangsettelsestillatelse</p>

<p vitec-if="Model.oppdrag.prosjekt.erutbyggersforbeholdbyggelaan == true">&#9745; byggelånet er åpnet</p>
<p vitec-if="Model.oppdrag.prosjekt.erutbyggersforbeholdbyggelaan != true">&#9744; byggelånet er åpnet</p>

<p>&#9744; endelig beslutning om igangsetting i utbyggers styre</p>

<p>De ovenfor nevnte forbehold gjelder for en periode på inntil <span class="insert">&nbsp;</span> måneder fra salgsstart, og selgers frist for å gjøre forbehold gjeldende er <span class="insert">&nbsp;</span>. Dersom selger ikke har sendt skriftlig melding til kjøper om at forbehold gjøres gjeldende innen fristen, er selger endelig juridisk bundet av kontrakten. Meldingen må angi hvilket forbehold som gjøres gjeldende, og må være kommet frem til kjøper innen den angitte frist per e-post eller rekommandert brev.</p>

<p>Dersom selger gjør forbehold gjeldende, gjelder følgende:</p>
<ul>
<li>Denne kjøpekontrakt bortfaller, med den virkning at ingen av partene kan gjøre krav gjeldende mot den annen part på grunnlag av kontraktens bestemmelser</li>
<li>Ethvert beløp som kjøper har innbetalt skal, inkludert opptjente renter, uten ugrunnet opphold tilbakeføres til kjøper</li>
</ul>
</article>

<!-- ===== SECTION 16 ===== -->
<article class="item">
<h2>ANNET</h2>

<p>Eventuell transport av denne kontrakt skal på forhånd aksepteres av selger og kan nektes på fritt grunnlag. Ved transport av kontrakt påløper et gebyr pålydende kr. <span class="insert">&nbsp;</span>,- Dersom denne kjøpekontrakt transporteres før ferdigstillelse, plikter den nye kjøperen å tre inn i alle de avtaler som er etablert, herunder endringsavtaler og tilvalgs bestillinger. Kjøper gjøres dog oppmerksom på at han hefter for dette kontraktsforhold inntil ny kjøper har signert alle dokumenter vedr. salget, og innbetalt kjøpesum inkl. omkostninger etter denne kontrakt. Kjøper har heller ikke anledning til å motsette seg overskjøting av boligen til seg, dersom han på overtakelsestidspunktet ikke har utpekt ny eier som har oppfylt kontrakts- og oppgjørsbestemmelsene i kjøpekontrakten. Transport av kontrakt kan senest skje 1 mnd. før overtagelse.</p>

<p>Det anbefales at [[meglerkontor.navn]] forestår transporten mot betaling i henhold til gjeldende standardsatser.</p>

<p>Ved besøk på byggeplassen før overtagelse skal kjøper alltid være i følge med en representant fra selger. All annen ferdsel på byggeplassen er beheftet med stor grad av risiko og er forbudt.</p>

<p>Selger forbeholder seg retten til enhver prisjustering på øvrige enheter i prosjektet. Uansett om prisforlangende for tilsvarende eierseksjon eller bolig i tidsrommet etter kontraktsinngåelsen blir justert opp eller ned, kan ingen av partene av den grunn kreve prisavslag eller pristillegg. Det samme gjelder om det blir avtalt høyere eller lavere pris på andre, tilsvarende seksjoner i prosjektet enn den pris som er avtalt i nærværende kontrakt.</p>

<p>Selger forbeholder seg retten til å forestå fordelingen av boder. Det samme gjelder fordelingen av garasjeplasser blant kjøpere som kjøper garasjeplass.</p>

<p>Selger forbeholder seg retten til å organisere parkering på den måte som anses mest hensiktsmessig, for eksempel som en del av sameiets fellesarealer, som tilleggsdel til seksjonene, andel av realsameie eller som en særskilt seksjon eller anleggseiendom (egen matrikkel). Utbygger tar forbehold om annen organisering av parkering dersom det skulle vise seg nødvendig eller hensiktsmessig.</p>

<p>Alle arealer er oppgitt som bruksareal (BRA) og samlet areal for primære rom (P-rom) i henhold til NS 3940. Bruksarealet er leilighetens totale innvendige areal inklusive bl.a. innvendige boder og kanalføringer.</p>
</article>

<!-- ===== SECTION 17 ===== -->
<article class="item">
<h2>SAMTYKKE TIL BRUK AV ELEKTRONISK KOMMUNIKASJON</h2>

<p>Avtalen mellom kjøper og selger er underlagt bestemmelsene i bustadoppføringslova. Der hvor denne avtalen eller der hvor Bustadoppføringslova setter krav til at meddelelser skal være skriftlig, er partene enige om at bruk av elektronisk kommunikasjon skal anses å oppfylle kravet til skriftlighet.</p>
</article>

<!-- ===== SECTION 18 ===== -->
<article class="item">
<h2>VERNETING</h2>

<p>Partene vedtar den faste eiendoms verneting som rett verneting for tvister etter denne kontrakt.</p>
</article>

<!-- ===== SECTION 19 ===== -->
<article class="item">
<h2>BILAG</h2>

<p>Kjøper er forelagt følgende dokumentasjon:</p>

<p>&#9744; Salgsoppgave</p>
<p>&#9744; Grunnboksutskrift for eiendommen</p>
<p>&#9744; Grunnboksutskrift for fellesarealer</p>
<p>&#9744; Utskrift av tinglyste erklæringer</p>
<p>&#9744; Reguleringsplan med reguleringsbestemmelser</p>
<p>&#9744; Opplysninger fra kommunen</p>
<p>&#9744; Målebrev/arealbekreftelse</p>
<p>&#9744; Ferdigattest/midlertidig brukstillatelse</p>
<p>&#9744; Protokoll for overtakelsesforretning</p>
<p>&#9744; Annet: <span class="insert">&nbsp;</span></p>
</article>

<!-- ===== SECTION 20 ===== -->
<article class="item avoid-page-break">
<h2>SIGNATUR</h2>

<p>Denne kontrakt er utferdiget i 3 &ndash; tre &ndash; likelydende eksemplar hvorav partene får hvert sitt eksemplar og ett beror hos eiendomsmegler.</p>

<p>Sted / Dato <span class="insert">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span> Sted / Dato</p>

<table style="width:100%; table-layout:fixed; border-collapse:collapse;">
<tbody>
<tr>
  <td colspan="40" style="border-bottom: solid 1px #000; padding: 4px 6px;">
    <p>Selger(e)</p>
    <p>&nbsp;</p>
    <p>&nbsp;</p>
  </td>
  <td colspan="20">&nbsp;</td>
  <td colspan="40" style="border-bottom: solid 1px #000; padding: 4px 6px;">
    <p>Kjøper(e)</p>
    <p>&nbsp;</p>
    <p>&nbsp;</p>
  </td>
</tr>
<tr>
  <td colspan="40">&nbsp;</td>
  <td colspan="20">&nbsp;</td>
  <td colspan="40" style="padding: 4px 6px;">[[kjoper.fullmektig.navn]]</td>
</tr>
</tbody>
</table>
</article>

</div>
"""

os.makedirs(OUTPUT_DIR, exist_ok=True)
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(TEMPLATE)

print(f"Written: {OUTPUT_FILE}")
print(f"Size: {len(TEMPLATE)} characters")
