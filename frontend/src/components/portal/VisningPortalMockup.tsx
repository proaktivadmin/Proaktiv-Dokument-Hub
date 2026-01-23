"use client";

import { PortalFrame } from "./PortalFrame";

/**
 * VisningPortalMockup Component
 * 
 * Pixel-accurate mockup of the Vitec Visningsportal (viewing registration portal) with Proaktiv branding.
 * Uses HTML structure consistent with Vitec's meglervisning.no portal.
 */

interface VisningPortalMockupProps {
  /** Whether to show financing option (for Voss office demo) */
  showFinancing?: boolean;
  /** Whether to show in fullscreen mode */
  fullscreen?: boolean;
  /** Whether to use vanilla (default) skin instead of Proaktiv skin */
  useVanillaSkin?: boolean;
}

export function VisningPortalMockup({ showFinancing = false, fullscreen = false, useVanillaSkin = false }: VisningPortalMockupProps) {
  // This HTML mirrors the Vitec Visningsportal structure from meglervisning.no
  const mockupHtml = `
<!-- Fixed header - matches Vitec structure -->
<header class="navbar navbar-expand-md bg-primary text-light fixed-top">
    <div class="object-header">
        <span>Visningspåmelding </span>
        <span class="d-none d-sm-inline"> - Fjellveien 42</span>
    </div>
</header>

<main class="position-relative" id="content" style="padding-top: 60px;">
    <!-- Property info section - bg-light text-dark matches Vitec -->
    <article class="info bg-light text-dark">
        <div class="container">
            <h1 class="header">
                <span>Meld deg på visning</span>
            </h1>
            <div class="row">
                <div class="col-12 col-lg-6">
                    <dl>
                        <dt>Adresse</dt>
                        <dd>
                            <span>Fjellveien 42</span>,
                            <span class="text-nowrap">
                                <span>5700</span>
                                <span>VOSS</span>
                            </span>
                        </dd>
                        <dt>Oppdragsnummer</dt>
                        <dd>1-0456/26</dd>
                    </dl>
                </div>
                <div class="col-12 col-lg-6">
                    <dl>
                        <dt>Ansvarlig megler</dt>
                        <dd>
                            <span>Per Hansen</span><br>
                            <span>Eiendomsmegler MNEF</span><br>
                            <strong>Telefon </strong>
                            <span>56 52 00 00</span>
                        </dd>
                    </dl>
                </div>
            </div>
        </div>
    </article>

    <!-- Viewing info section - bg-info matches Vitec -->
    <article class="container primary bg-info status">
        <h2>Visningsinformasjon</h2>
        <div class="list-group">
            <div class="list-group-item">
                <div class="d-flex align-items-center">
                    <i class="far fa-calendar-alt mr-3" style="font-size: 24px;"></i>
                    <div>
                        <strong>Søndag 26. januar 2026</strong><br>
                        <span>kl. 12:00 - 13:00</span>
                    </div>
                </div>
            </div>
        </div>
        <p class="mt-3 small">
            <i class="fas fa-info-circle mr-1"></i>
            Du vil motta en bekreftelse på e-post etter påmelding.
        </p>
    </article>

    <!-- Registration form section -->
    <article class="container primary">
        <h2 class="header">
            <span>Dine opplysninger</span>
        </h2>
        <p aria-hidden="true">
            <span class="required-mark">*</span>
            <span>Stjernemerkede felt må fylles ut</span>
        </p>

        <fieldset>
            <legend class="position-relative">
                <span>Personopplysninger</span>
            </legend>

            <div class="alert alert-outline-bordered">
                <div class="form-row">
                    <div class="col-12 col-md-6 form-group">
                        <label for="FirstName">
                            <span>Fornavn</span>
                            <span class="required-mark" aria-hidden="true">*</span>
                        </label>
                        <input class="form-control" type="text" id="FirstName" value="Kari">
                    </div>
                    <div class="col-12 col-md-6 form-group">
                        <label for="LastName">
                            <span>Etternavn</span>
                            <span class="required-mark" aria-hidden="true">*</span>
                        </label>
                        <input class="form-control" type="text" id="LastName" value="Nordmann">
                    </div>
                </div>
                <div class="form-row">
                    <div class="col-12 col-md-6 form-group">
                        <label for="Phone">
                            <span>Mobiltelefon</span>
                            <span class="required-mark" aria-hidden="true">*</span>
                        </label>
                        <input class="form-control" type="tel" id="Phone" value="+47 912 34 567">
                        <span class="helper-text">Må være et norsk mobilnummer</span>
                    </div>
                    <div class="col-12 col-md-6 form-group">
                        <label for="NumberOfPeople">
                            <span>Antall personer</span>
                            <span class="required-mark" aria-hidden="true">*</span>
                        </label>
                        <select class="form-control" id="NumberOfPeople">
                            <option>1</option>
                            <option selected>2</option>
                            <option>3</option>
                            <option>4+</option>
                        </select>
                    </div>
                </div>
                <div class="form-row">
                    <div class="col-12 form-group">
                        <label for="Email">
                            <span>E-postadresse</span>
                            <span class="required-mark" aria-hidden="true">*</span>
                        </label>
                        <input class="form-control" type="email" id="Email" value="kari.nordmann@eksempel.no">
                    </div>
                </div>
            </div>
        </fieldset>

        <fieldset>
            <legend class="position-relative">
                <span>Ønsker</span>
            </legend>

            <div class="alert alert-outline-bordered">
                <p class="mb-3">Hvis du ønsker videre oppfølging på eiendommen, kan du krysse av for følgende:</p>

                <!-- Consent options - EXACT Vitec structure -->
                <div class="form-row">
                    ${showFinancing ? `
                    <div class="col-12 form-group">
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
                        <small class="form-text text-muted ml-4">Din kontaktinformasjon sendes til en bankrådgiver.</small>
                    </div>
                    ` : ''}
                    <div class="col-12 form-group">
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
                        <small class="form-text text-muted ml-4">En eiendomsmegler vil kontakte deg for å avtale tid.</small>
                    </div>
                    <div class="col-12 form-group">
                        <label class="with-input">
                            <span>
                                <input type="checkbox" id="consentBidInfo" checked>
                                <span>Ja, jeg ønsker å bli varslet om bud på eiendommen</span>
                            </span>
                            <a class="consent-link" href="#" title="Les mer">
                                <span class="link-text">Les mer</span>
                                <i aria-hidden="true" class="far fa-question-circle"></i>
                            </a>
                        </label>
                        <small class="form-text text-muted ml-4">Du registreres som interessent og varsles om bud.</small>
                    </div>
                    <!-- Newsletter hidden per Proaktiv config -->
                    <div class="col-12 form-group">
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
                        <small class="form-text text-muted ml-4">Få varsel når nye boliger matcher dine ønsker.</small>
                    </div>
                </div>
            </div>
        </fieldset>

        <fieldset>
            <legend class="position-relative">
                <span>Salgsoppgave</span>
            </legend>

            <div class="alert alert-outline-bordered">
                <div class="form-row">
                    <div class="col-12 form-group">
                        <label class="with-input">
                            <span>
                                <input type="checkbox" id="getSalesDoc" checked>
                                <span>Ja, send meg salgsoppgaven på e-post</span>
                            </span>
                        </label>
                    </div>
                </div>
            </div>
        </fieldset>

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
                    <span>Meld meg på visning</span>
                    <i class="fas fa-check ml-2"></i>
                </button>
            </div>
        </div>
    </article>

    <!-- Broker info section -->
    <article class="container primary bg-light">
        <div class="row align-items-center">
            <div class="col-auto">
                <div class="rounded-circle bg-secondary d-flex align-items-center justify-content-center" style="width: 64px; height: 64px;">
                    <i class="fas fa-user text-light" style="font-size: 28px;"></i>
                </div>
            </div>
            <div class="col">
                <h4 class="mb-0">Per Hansen</h4>
                <p class="mb-0 text-muted">Eiendomsmegler MNEF</p>
                <p class="mb-0">
                    <i class="fas fa-phone mr-1"></i> 56 52 00 00
                    <span class="mx-2">|</span>
                    <i class="fas fa-envelope mr-1"></i> per.hansen@proaktiv.no
                </p>
            </div>
        </div>
    </article>

    <!-- Footer -->
    <footer class="container text-center py-4">
        <p class="small text-muted mb-0">
            Proaktiv Eiendomsmegling
        </p>
    </footer>
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
  const skinCssHref = useVanillaSkin ? undefined : "/skins/proaktiv-visning.css";

  return (
    <PortalFrame
      content={mockupHtml}
      skinCssHref={skinCssHref}
      title={useVanillaSkin ? "Visningsportal - Vanilla" : "Visningsportal - Proaktiv"}
      minHeight={fullscreen ? "100vh" : "1000px"}
      portalType="visning"
    />
  );
}
