"use client";

import { PortalFrame } from "./PortalFrame";

/**
 * VisningPortalMockup Component
 *
 * Pixel-accurate mockup of the Vitec Visningsportal (viewing registration portal) with Proaktiv branding.
 * Uses the EXACT HTML structure scraped from the live meglervisning.no portal.
 *
 * Source: Live Vitec portal HTML (MSPROA/Proaktiv)
 */

interface VisningPortalMockupProps {
  /** Whether to show financing option (for Voss office demo) */
  showFinancing?: boolean;
  /** Whether to show in fullscreen mode */
  fullscreen?: boolean;
  /** Whether to use vanilla (default) skin instead of Proaktiv skin */
  useVanillaSkin?: boolean;
}

export function VisningPortalMockup({
  showFinancing = false,
  fullscreen = false,
  useVanillaSkin = false,
}: VisningPortalMockupProps) {
  // This HTML mirrors the EXACT Vitec Visningsportal structure from meglervisning.no
  const mockupHtml = `
<!-- Background image from property listing -->
<picture class="background-image">
    <source media="(min-width: 1025px)" srcset="/assets/visning-demo-bg.jpg">
    <source media="(max-width: 1024px)" srcset="/assets/visning-demo-bg.jpg">
    <img src="/assets/visning-demo-bg.jpg" alt="" aria-hidden="true">
</picture>

<div class="container main" aria-live="polite" aria-busy="false">
    <div class="row">
        <div class="col-sm-12">
            <h1 class="text-left">
                <strong>Visning</strong>
                <span>Dyrnesvika 18</span>
            </h1>
        </div>
    </div>

    <!-- Visningstid selection -->
    <div class="form-group">
        <fieldset>
            <legend>
                <span>Visningstid</span>
            </legend>
            <div>
                <button class="btn btn-sm mb-1 btn-outline-primary btn-primary text-light">
                    <i class="far mr-1 fa-check-square" aria-hidden="true"></i>
                    <span>søndag 26. januar kl 12:00 - 13:00</span>
                    <span class="sr-only"> (valgt)</span>
                </button>
            </div>
        </fieldset>
    </div>

    <!-- Participants selection -->
    <div class="form-group">
        <fieldset>
            <legend class="participants">Hvor mange deltar?</legend>
            <div>
                <button class="btn btn-sm mb-1 btn-outline-primary btn-primary text-light">
                    <i class="far mr-1 fa-check-square" aria-hidden="true"></i>
                    <span>1 person</span>
                    <span class="sr-only"> (valgt)</span>
                </button>
                <button class="btn btn-sm mb-1 btn-outline-primary">
                    <i class="far mr-1 fa-square" aria-hidden="true"></i>
                    <span>2 personer</span>
                </button>
                <button class="btn btn-sm mb-1 btn-outline-primary">
                    <i class="far mr-1 fa-square" aria-hidden="true"></i>
                    <span>3 personer</span>
                </button>
                <button class="btn btn-sm mb-1 btn-outline-primary">
                    <i class="far mr-1 fa-square" aria-hidden="true"></i>
                    <span>4 personer</span>
                </button>
                <button class="btn btn-sm mb-1 btn-outline-primary">
                    <i class="far mr-1 fa-square" aria-hidden="true"></i>
                    <span>5 personer</span>
                </button>
            </div>
        </fieldset>
    </div>

    <!-- Personal information form -->
    <div class="row">
        <div class="col-sm-12">
            <fieldset>
                <legend>Dine opplysninger</legend>
                <div class="form-row">
                    <div class="col-sm-12 col-md-6 col-lg-4 form-group">
                        <label for="txt_phone" class="required-field">
                            <span>Mobiltelefon</span>
                            <small aria-hidden="true"> (må fylles ut)</small>
                        </label>
                        <div class="input-group">
                            <div class="input-group-prepend" aria-hidden="true">
                                <div class="input-group-text"><i class="fas fa-search"></i></div>
                            </div>
                            <input class="form-control" placeholder="Søk kontakt" autocomplete="off" name="PhoneNumber" id="txt_phone" type="tel" maxlength="12" required value="+47 912 34 567">
                        </div>
                    </div>
                    <div class="col-sm-12 col-md-6 col-lg-3 form-group">
                        <label for="txt_firstname" class="required-field">
                            <span>Fornavn</span>
                            <small aria-hidden="true"> (må fylles ut)</small>
                        </label>
                        <input class="form-control" name="FirstName" id="txt_firstname" autocomplete="off" type="text" maxlength="63" required value="Kari">
                    </div>
                    <div class="col-sm-12 col-md-6 col-lg-5 form-group">
                        <label for="txt_surname" class="required-field">
                            <span>Etternavn</span>
                            <small aria-hidden="true"> (må fylles ut)</small>
                        </label>
                        <input class="form-control" name="LastName" id="txt_surname" autocomplete="off" type="text" maxlength="63" required value="Nordmann">
                    </div>
                    <div class="col-sm-12 col-md-6 col-lg-4 form-group">
                        <label for="txt_email">E-postadresse</label>
                        <input class="form-control" name="Email" id="txt_email" type="email" autocomplete="off" maxlength="63" value="kari.nordmann@eksempel.no">
                    </div>
                    <div class="col-sm-12 col-md-6 col-lg-3 form-group">
                        <label for="txt_address">Adresse</label>
                        <input class="form-control" name="Address" id="txt_address" autocomplete="off" type="text" maxlength="63" value="Eksempelveien 1">
                    </div>
                    <div class="col-sm-12 col-md-6 col-lg-5">
                        <div class="form-row d-none d-sm-block">
                            <div class="col-sm-12">
                                <label for="txt_zip">
                                    <span>Postnummer og -sted</span>
                                </label>
                            </div>
                        </div>
                        <div class="form-row">
                            <div class="col-sm-4 col-md-5 col-lg-4 form-group">
                                <label for="txt_zip" class="d-block d-sm-none">
                                    <span>Postnummer</span>
                                </label>
                                <input class="form-control" name="ZipCode" id="txt_zip" autocomplete="off" type="text" maxlength="4" value="5700">
                            </div>
                            <div class="col-sm-8 col-md-7 col-lg-8 form-group">
                                <label for="txt_city" class="d-block d-sm-none">Poststed</label>
                                <input class="form-control" name="City" id="txt_city" autocomplete="off" type="text" readonly value="VOSS">
                            </div>
                        </div>
                    </div>
                </div>
            </fieldset>
        </div>
    </div>

    <!-- Consent section -->
    <fieldset>
        <legend>Samtykke og valg</legend>

        <div class="form-row">
            <div class="col-sm-12">
                <div class="check-option">
                    <input type="checkbox" id="chk_AcceptTerms" name="AcceptTerms" value="true" checked>
                    <label for="chk_AcceptTerms">
                        <span>
                            <span>Jeg aksepterer at mine opplysninger lagres hos meglerforetaket og at jeg vil motta relevant informasjon om eiendommen.</span>
                            <a class="consent-link" data-toggle="modal" data-target="#modal1" href="#">
                                <span class="link-text">Les mer</span> <i aria-hidden="true" class="far fa-question-circle"></i>
                            </a>
                        </span>
                    </label>
                </div>
            </div>
        </div>

        <!-- Newsletter - hidden per Proaktiv config, but shown in mockup for demo -->
        <div class="form-row" style="display: none;">
            <div class="col-sm-12">
                <div class="check-option">
                    <input type="checkbox" id="chk_NewsLetter" name="NewsLetter" value="true" disabled>
                    <label for="chk_NewsLetter">
                        <span>
                            <span>Jeg ønsker å abonnere på nyhetsbrev</span>
                        </span>
                    </label>
                </div>
            </div>
        </div>

        <!-- Financing - only shown for Voss office -->
        ${
          showFinancing
            ? `
        <div class="form-row">
            <div class="col-sm-12">
                <div class="check-option">
                    <input type="checkbox" id="chk_consentsContactForFinance" name="consentsContactForFinance" value="true">
                    <label for="chk_consentsContactForFinance">
                        <span>
                            <span>Jeg ønsker tilbud om finansiering</span>
                        </span>
                    </label>
                </div>
            </div>
        </div>
        `
            : ""
        }

        <!-- Verdivurdering -->
        <div class="form-row">
            <div class="col-sm-12">
                <div class="check-option">
                    <input type="checkbox" id="chk_consentsContactForOwnEstate" name="consentsContactForOwnEstate" value="true" checked>
                    <label for="chk_consentsContactForOwnEstate">
                        <span>
                            <span>Jeg ønsker verdivurdering av min bolig</span>
                        </span>
                    </label>
                </div>
            </div>
        </div>

        <!-- Buttons -->
        <div class="form-row">
            <div class="col-sm-12 col-md-6 form-group">
            </div>
            <div class="col-sm-12 col-md-6 text-right">
                <button class="btn btn-primary btn-lg">Nullstill</button>
                <button class="btn btn-primary btn-lg" id="saveContact" name="action">Registrer</button>
            </div>
        </div>
    </fieldset>
</div>

<!-- Footer -->
<footer class="container footer">
    <div>
        © 2026 <span>- Vitec Megler Visningsportal</span>
        v.1.2.4.3
        <a href="#" id="reopenCookieBanner">Endre valg for informasjonskapsler</a>
    </div>
</footer>

<!-- Privacy modal -->
<div class="modal" id="modal1" tabindex="-1" role="dialog" aria-labelledby="modal1Label" aria-hidden="true">
    <div class="modal-dialog" role="document">
        <div class="modal-content">
            <div class="modal-header">
                <h1 class="modal-title" id="modal1Label">Personvern</h1>
                <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                    <span aria-hidden="true">×</span>
                </button>
            </div>
            <div class="modal-body">
                <h2>Mine opplysninger</h2>
                <p>Hensikten med denne registreringen er å tilby deg relevant og ønsket informasjon fra meglerforetaket.</p>
                <p>Meglerforetaket plikter å oppbevare dine opplysninger på en forsvarlig måte og følge gjeldende lover og forskrifter om vern av personopplysninger.</p>
                <p>Les mer om personvern på <a href="https://proaktiv.no/personvern" target="_blank" rel="noopener">proaktiv.no/personvern</a></p>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-primary" data-dismiss="modal">
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
