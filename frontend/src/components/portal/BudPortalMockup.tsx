"use client";

import { PortalFrame } from "./PortalFrame";

/**
 * BudPortalMockup Component
 * 
 * Pixel-accurate mockup of the Vitec Budportal (bidding portal) with Proaktiv branding.
 * Uses the EXACT HTML structure and CSS classes from the live Vitec portal.
 * 
 * Source: Live Vitec portal HTML (MSNOP/Nordvik Bolig)
 */

interface BudPortalMockupProps {
  /** Whether to show financing option (for Voss office demo) */
  showFinancing?: boolean;
  /** Whether to show in fullscreen mode */
  fullscreen?: boolean;
  /** Whether to use vanilla (default) skin instead of Proaktiv skin */
  useVanillaSkin?: boolean;
}

export function BudPortalMockup({ showFinancing = false, fullscreen = false, useVanillaSkin = false }: BudPortalMockupProps) {
  // This HTML mirrors the EXACT Vitec Budportal structure from bud.vitecnext.no
  const mockupHtml = `
<!-- Fixed header - matches Vitec structure -->
<header class="navbar navbar-expand-md bg-primary text-light fixed-top">
    <div class="object-header">
        <span>Gi bud </span>
        <span class="d-none d-sm-inline"> på Strandgata 15A</span>
    </div>
    <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
        <i class="fas fa-bars text-light"></i>
    </button>
    <div class="collapse navbar-collapse" id="navbarNav">
        <nav id="stepNav">
            <ul class="nav nav-pills">
                <li class="nav-item">
                    <a class="nav-link btn-sm btn-outline-light" href="#Buddetaljer">
                        <span>Buddetaljer</span>
                    </a>
                </li>
                <li class="nav-item">
                    <a class="nav-link btn-sm btn-outline-light" href="#Budgiver">
                        <span>Budgiver</span>
                    </a>
                </li>
                ${showFinancing ? `
                <li class="nav-item">
                    <a class="nav-link btn-sm btn-outline-light" href="#Finansiering">
                        <span>Finansiering</span>
                    </a>
                </li>
                ` : ''}
            </ul>
        </nav>
    </div>
</header>

<main class="position-relative" id="content" style="padding-top: 60px;">
    <!-- Property info section - bg-light text-dark matches Vitec -->
    <article class="info bg-light text-dark">
        <div class="container">
            <h1 class="header">
                <span>Gi bud på Strandgata 15A</span>
            </h1>
            <div class="row">
                <div class="col-12 col-lg-4">
                    <dl>
                        <dt>Adresse</dt>
                        <dd>
                            <span>Strandgata 15A</span>,
                            <span class="text-nowrap">
                                <span>5700</span>
                                <span>VOSS</span>
                            </span>
                        </dd>
                        <dt>Oppdragsnummer</dt>
                        <dd>1-0123/26</dd>
                        <dt>Matrikkel</dt>
                        <dd>Gnr: 123, Bnr: 45, Snr: 1, i Voss herad</dd>
                    </dl>
                </div>
                <div class="col-12 col-lg-4">
                    <dl>
                        <dt>Ansvarlig megler</dt>
                        <dd>
                            <span>Per Hansen</span><br>
                            <span>Eiendomsmegler MNEF</span><br>
                            <strong>Telefon </strong>
                            <span>56 52 00 00</span><br>
                            <strong>E-postadresse </strong>
                            <a class="break-word" href="mailto:per.hansen@proaktiv.no">per.hansen@proaktiv.no</a>
                        </dd>
                    </dl>
                </div>
                <div class="col-12 col-lg-4">
                    <dl>
                        <dt>Saksbehandler</dt>
                        <dd>
                            <span>Per Hansen</span><br>
                            <span>Eiendomsmegler MNEF</span><br>
                            <strong>Telefon </strong>
                            <span>56 52 00 00</span><br>
                            <strong>E-postadresse </strong>
                            <a class="break-word" href="mailto:per.hansen@proaktiv.no">per.hansen@proaktiv.no</a>
                        </dd>
                    </dl>
                </div>
            </div>
        </div>
    </article>

    <!-- Important info section - bg-info matches Vitec -->
    <article class="container primary bg-info status">
        <h2>Viktig informasjon</h2>
        <p>
            <span>Før du gir bud må du</span>
            <strong>bekrefte at du har lest salgs­oppgave</strong>
            <span>og sette deg inn i retnings­linjer som beskrevet hos Forbruker­tilsynet.</span>
        </p>
        <div class="list-group">
            <a class="list-group-item list-group-item-action" href="#" target="_blank" rel="noopener" title="PDF-dokument">
                <span>
                    <i class="far fa-arrow-alt-square-down" aria-hidden="true"></i>
                    <span class="link-text">Last ned salgsoppgave</span>
                </span>
                <small>
                    <span>Dokument opprettet </span>
                    <span>22.01.2026 - 10:00</span>
                </small>
            </a>
            <a class="list-group-item list-group-item-action" target="_blank" rel="noopener" title="Åpne i ny fane" href="https://nef.no/wp-content/uploads/2025/06/Forbrukerinformasjon-om-budgivning_oppdatert-pr.-1.-juli-2025.pdf">
                <span>
                    <i class="far fa-external-link-square-alt" aria-hidden="true"></i>
                    <span class="link-text">Les Forbruker­informasjon om budgivning</span>
                </span>
                <small>
                    <span>nef.no</span>
                </small>
            </a>
        </div>
    </article>

    <!-- Main form section -->
    <article class="container primary">
        <h2 class="header">
            <span>Lag budskjema</span>
        </h2>
        <p>Når budskjemaet er opprettet skal det signeres med bankID av budgiver før budet sendes til megler for godkjenning og journalføring.</p>
        <p>Signering ved Bank-ID er juridisk bindende signatur og budgiver aksepterer at e-signering med Bank-ID benyttes som signatur i anledning dette budet.</p>
        <p aria-hidden="true">
            <span class="required-mark">*</span>
            <span>Stjernemerkede felt må fylles ut</span>
        </p>

        <!-- Buddetaljer fieldset -->
        <fieldset>
            <legend class="position-relative">
                <span>Buddetaljer</span>
                <a class="scroll-target" id="Buddetaljer">&nbsp;</a>
            </legend>
            <div class="form-row">
                <div class="col-12 col-md-12">
                    <div class="alert alert-info" id="expiresTimeManualInstruction">
                        <strong>Akseptfrist</strong><br>
                        <span>Megler formidler ikke bud med kortere akseptfrist enn 12:00 første virkedag etter siste annonserte visning.</span>
                    </div>
                </div>
                <div class="col-12 col-md-6 col-lg-4 form-group">
                    <label for="bidAmount">
                        <span>Budbeløp</span>
                        <span class="required-mark" aria-hidden="true">*</span>
                    </label>
                    <input class="form-control" id="bidAmount" type="text" value="4 500 000" title="Budbeløp må fylles ut">
                </div>
                <div class="col-12 col-md-12 col-lg-8">
                    <div class="form-row">
                        <div class="col-12 col-md-6 form-group">
                            <label for="expiresDateManual">
                                <span>Akseptfrist dato</span>
                                <span class="required-mark" aria-hidden="true">*</span>
                            </label>
                            <div class="input-group">
                                <input id="expiresDateManual" type="text" class="form-control" placeholder="dd.mm.åååå" value="24.01.2026">
                                <div class="input-group-append">
                                    <span class="input-group-text" title="Velg dato ..."><i class="far fa-calendar-alt"></i></span>
                                </div>
                            </div>
                        </div>
                        <div class="col-12 col-md-6 form-group">
                            <label for="expiresTimeManual">
                                <span>Akseptfrist klokkeslett</span>
                                <span class="required-mark" aria-hidden="true">*</span>
                            </label>
                            <input id="expiresTimeManual" type="text" class="form-control" placeholder="tt:mm" value="12:00">
                        </div>
                    </div>
                </div>
            </div>
            <div class="form-row">
                <div class="col-12 form-group">
                    <label for="WantedTakeover">Overtakelse</label><br>
                    <textarea class="form-control" id="WantedTakeover" placeholder="Maksimalt 63 tegn">01.03.2026</textarea>
                    <span class="helper-text">Eventuell dato du ønsker å overta eiendommen.</span>
                </div>
            </div>
            <div class="form-row" id="reservationsContainer">
                <div class="col-12 form-group">
                    <label for="Reservations">Forbehold</label>
                    <textarea class="form-control" id="Reservations" placeholder="Forbehold..."></textarea>
                </div>
                <div class="col-12">
                    <div class="alert alert-warning" id="ReservationsInstruction">
                        <strong>Forbehold</strong><br>
                        <ul>
                            <li>Ikke skriv personopplysninger i dette feltet.</li>
                            <li>Forbehold du oppgir her, blir en del av budet og videreformidles til selger, andre budgivere og interessenter.</li>
                        </ul>
                    </div>
                </div>
            </div>
        </fieldset>

        <!-- Budgiver fieldset -->
        <fieldset>
            <legend class="position-relative">
                <span>Budgiver </span>
                <span>1</span>
                <span> (innsender)</span>
                <div class="alert alert-warning contact-verification-info mt-3">
                    <strong>Bekreft mobil eller e-post</strong>
                    <p>Budgiver 1 må bekrefte registrert mobiltelefon eller e-postadresse. Dette gjøres nederst i skjemaet før budskjema opprettes.</p>
                </div>
                <a class="scroll-target" id="Budgiver">&nbsp;</a>
            </legend>

            <!-- Consumer/business declaration -->
            <div class="alert alert-outline-bordered">
                <p>
                    <strong>Egenerklæring fra budgiver</strong>
                </p>
                <div class="form-check mb-2 cb-container">
                    <input class="form-check-input" type="radio" name="bidderType" id="isConsumer" checked>
                    <label class="form-check-label" for="isConsumer">Jeg er en fysisk person, og handler som forbruker</label>
                </div>
                <div class="form-check mb-2 cb-container">
                    <input class="form-check-input" type="radio" name="bidderType" id="isBusiness">
                    <label class="form-check-label" for="isBusiness">Jeg handler som ledd i næringsvirksomhet</label>
                </div>
            </div>

            <!-- Personal info -->
            <div class="alert alert-outline-bordered">
                <div class="mb-3">
                    <strong>Personopplysninger</strong>
                </div>
                <div class="form-row">
                    <div class="col-12 col-md-6 form-group">
                        <label for="FirstName0">
                            <span>Fornavn</span>
                            <span class="required-mark" aria-hidden="true">*</span>
                        </label>
                        <input class="form-control" type="text" id="FirstName0" value="Ola">
                    </div>
                    <div class="col-12 col-md-6 form-group">
                        <label for="LastName0">
                            <span>Etternavn</span>
                            <span class="required-mark" aria-hidden="true">*</span>
                        </label>
                        <input class="form-control" type="text" id="LastName0" value="Nordmann">
                    </div>
                </div>
                <div class="form-row">
                    <div class="col-12 col-md-6 form-group">
                        <label for="Ssn0">
                            <span>Fødselsnummer</span>
                            <span class="required-mark" aria-hidden="true">*</span>
                        </label>
                        <input class="form-control" type="text" id="Ssn0" value="01019012345" autocomplete="off">
                    </div>
                    <div class="col-12 col-md-6 form-group">
                        <label for="Phone0">
                            <span>Mobiltelefon</span>
                            <span class="required-mark" aria-hidden="true">*</span>
                        </label>
                        <input class="form-control" type="tel" id="Phone0" value="+47 987 65 432">
                        <span class="helper-text">Må være et norsk mobilnummer</span>
                    </div>
                </div>
                <div class="form-row">
                    <div class="col-12 form-group">
                        <label for="Email0">
                            <span>E-postadresse</span>
                            <span class="required-mark" aria-hidden="true">*</span>
                        </label>
                        <input class="form-control" type="email" id="Email0" value="ola.nordmann@eksempel.no">
                    </div>
                </div>
                <div class="form-row">
                    <div class="col-12 form-group">
                        <label for="Address0">
                            <span>Adresse</span>
                            <span class="required-mark" aria-hidden="true">*</span>
                        </label>
                        <input class="form-control" type="text" id="Address0" value="Eksempelveien 1">
                    </div>
                </div>
                <div class="form-row form-group">
                    <div class="col-12 col-md-3 col-lg-2 form-group">
                        <label for="Zip0">
                            <span>Postnummer</span>
                            <span class="required-mark" aria-hidden="true">*</span>
                        </label>
                        <input class="form-control" type="text" id="Zip0" value="5700">
                    </div>
                    <div class="col-12 col-md-9 col-lg-10 form-group">
                        <label for="City0">
                            <span>Poststed</span>
                        </label>
                        <input class="form-control" type="text" id="City0" value="VOSS" readonly>
                    </div>
                </div>

                <!-- Consent options - EXACT Vitec structure -->
                <div class="form-row">
                    ${showFinancing ? `
                    <div class="col-12 col-lg-6 form-group">
                        <label class="with-input">
                            <span>
                                <input type="checkbox" id="consentFinancing">
                                <span>Ja, jeg ønsker et tilbud på finansiering</span>
                            </span>
                            <a class="consent-link" href="#" title="Les mer">
                                <span class="link-text">Les mer</span>
                                <i aria-hidden="true" class="far fa-question-circle"></i>
                            </a>
                        </label>
                    </div>
                    ` : ''}
                    <div class="col-12 col-lg-6 form-group">
                        <label class="with-input">
                            <span>
                                <input type="checkbox" id="consentFollowup" checked>
                                <span>Ja, jeg ønsker en verdivurdering av boligen min</span>
                            </span>
                            <a class="consent-link" href="#" title="Les mer">
                                <span class="link-text">Les mer</span>
                                <i aria-hidden="true" class="far fa-question-circle"></i>
                            </a>
                        </label>
                    </div>
                    <!-- Newsletter hidden per Proaktiv config -->
                    <div class="col-12 col-lg-6 form-group">
                        <label class="with-input">
                            <span>
                                <input type="checkbox" id="consentSearchProfile">
                                <span>Ja, jeg ønsker å opprette en søkeprofil</span>
                            </span>
                            <a class="consent-link" href="#" title="Les mer">
                                <span class="link-text">Les mer</span>
                                <i aria-hidden="true" class="far fa-question-circle"></i>
                            </a>
                        </label>
                    </div>
                </div>
            </div>
        </fieldset>

        ${showFinancing ? `
        <!-- Finansiering fieldset - only shown for Voss office -->
        <fieldset>
            <legend class="position-relative">
                <span>Finansiering</span>
                <a class="scroll-target" id="Finansiering">&nbsp;</a>
            </legend>
            <div class="form-row">
                <div class="col-12 form-group">
                    <label for="usingNorwegianBank" class="with-input">
                        <input type="checkbox" id="usingNorwegianBank" checked>
                        <span>Finansiering i norsk bank</span>
                    </label>
                </div>
            </div>
            <div class="form-row">
                <div class="col-12 col-md-4 form-group">
                    <label for="bank">
                        <span>Bank</span>
                        <span class="required-mark" aria-hidden="true">*</span>
                    </label>
                    <select class="form-control" id="bank">
                        <option value="">Velg bank</option>
                        <option>DNB</option>
                        <option selected>SPAREBANK 1</option>
                        <option>NORDEA</option>
                        <option>HANDELSBANKEN</option>
                    </select>
                </div>
                <div class="col-12 col-md-4 form-group">
                    <label for="bankContactPersonName">
                        <span>Kontaktperson</span>
                        <span class="required-mark" aria-hidden="true">*</span>
                    </label>
                    <input class="form-control" type="text" id="bankContactPersonName" value="Kari Banksen">
                </div>
                <div class="col-12 col-md-4 form-group">
                    <label for="bankContactPersonPhone">
                        <span>Telefon</span>
                        <span class="required-mark" aria-hidden="true">*</span>
                    </label>
                    <input class="form-control" type="tel" id="bankContactPersonPhone" value="+47 555 12 345">
                </div>
            </div>
        </fieldset>
        ` : ''}

        <!-- Add bidder button -->
        <div class="row">
            <div class="col-12">
                <div class="alert alert-info">
                    <button class="btn btn-primary add-bidder-button">
                        <span>Legg til budgiver 2</span>
                    </button>
                    <div class="mt-2">Undertegnede budgivere (hvis flere) gir hverandre gjensidig representasjonsfullmakt.</div>
                </div>
            </div>
        </div>

        <!-- Privacy and submit -->
        <div class="form-row mt-4">
            <div class="col-12">
                <p class="small">
                    Les om hvordan vi behandler personopplysninger på 
                    <a href="https://proaktiv.no/personvern" target="_blank" rel="noopener">proaktiv.no/personvern</a>
                </p>
            </div>
        </div>

        <div class="form-row">
            <div class="col-12">
                <button class="btn btn-primary btn-lg btn-block" type="submit">
                    <span>Opprett budskjema</span>
                    <i class="fas fa-arrow-right ml-2"></i>
                </button>
            </div>
        </div>
    </article>
</main>

<!-- Modal for consent info (example) -->
<div class="modal fade" id="modal1" tabindex="-1" role="dialog" aria-hidden="true">
    <div class="modal-dialog" role="document">
        <div class="modal-content">
            <div class="modal-header">
                <h1 class="modal-title">Personvern</h1>
                <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                    <span aria-hidden="true">&times;</span>
                </button>
            </div>
            <div class="modal-body">
                <p>Eiendomsmeglerforetaket behandler personopplysninger som er nødvendige for å oppfylle avtalen med deg. Les mer om hvordan vi behandler personopplysninger i personvernserklæringen på <a rel="noopener" target="_blank" href="https://proaktiv.no/personvern">proaktiv.no/personvern</a></p>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-dismiss="modal">
                    <span>Lukk</span>
                </button>
            </div>
        </div>
    </div>
</div>
`;

  // Vanilla skin uses no custom CSS (just Bootstrap defaults)
  // Proaktiv skin uses the custom branded CSS
  const skinCssHref = useVanillaSkin ? undefined : "/skins/proaktiv-bud.css";

  return (
    <PortalFrame
      content={mockupHtml}
      skinCssHref={skinCssHref}
      title={useVanillaSkin ? "Budportal - Vanilla" : "Budportal - Proaktiv"}
      minHeight={fullscreen ? "100vh" : "1200px"}
      portalType="bud"
    />
  );
}
