"use client";

import { PortalFrame } from "./PortalFrame";

/**
 * SalgsoppgavePortalMockup Component
 *
 * Pixel-accurate mockup of the Vitec "Bestill salgsoppgave" (Order Property Description) portal
 * with Proaktiv branding. Uses the EXACT HTML structure scraped from the live meglervisning.no portal.
 *
 * This portal shares the same skin as Visningsportal but has a simpler form focused on
 * receiving the property description PDF via email.
 *
 * Source: Live Vitec portal HTML (MSPROA/Proaktiv)
 */

interface SalgsoppgavePortalMockupProps {
  /** Whether to show financing option (for Voss office demo) */
  showFinancing?: boolean;
  /** Whether to show in fullscreen mode */
  fullscreen?: boolean;
  /** Whether to use vanilla (default) skin instead of Proaktiv skin */
  useVanillaSkin?: boolean;
}

export function SalgsoppgavePortalMockup({
  showFinancing = false,
  fullscreen = false,
  useVanillaSkin = false,
}: SalgsoppgavePortalMockupProps) {
  // This HTML mirrors the EXACT Vitec "Bestill salgsoppgave" structure from meglervisning.no
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
                <strong>Bestill salgsoppgave</strong>
                <br class="d-md-none">
                <span>Dyrnesvika 18</span>
            </h1>
        </div>
    </div>

    <div class="row">
        <div class="col-sm-12">
            <fieldset role="status">
                <legend>Dine opplysninger</legend>
                
                <!-- Email field - primary required field -->
                <div class="row">
                    <div class="col-sm-12 col-md-12 col-lg-6 form-group">
                        <label for="txt_email" class="required-field">
                            <span>E-postadresse</span>
                            <small> (må fylles ut)</small>
                        </label>
                        <input class="form-control" name="Email" id="txt_email" type="email" autocomplete="off" maxlength="63" value="kari.nordmann@eksempel.no">
                    </div>
                </div>
                
                <!-- Optional contact info section -->
                <div class="alert alert-info">
                    <p>Hvis du ønsker videre oppfølging på eiendommen trenger vi mer informasjon:</p>
                    
                    <div class="row form-row">
                        <div class="col-sm-12 col-md-6 col-lg-4 form-group">
                            <label for="txt_firstname" class="required-field">
                                <span>Fornavn</span>
                            </label>
                            <input class="form-control" name="FirstName" id="txt_firstname" autocomplete="off" type="text" maxlength="63" value="Kari">
                        </div>
                        <div class="col-sm-12 col-md-6 col-lg-4 form-group">
                            <label for="txt_surname" class="required-field">
                                <span>Etternavn</span>
                            </label>
                            <input class="form-control" name="LastName" id="txt_surname" autocomplete="off" type="text" maxlength="63" value="Nordmann">
                        </div>
                        <div class="col-sm-12 col-md-6 col-lg-2 form-group">
                            <label for="txt_phone" class="required-field">
                                <span>Mobiltelefon</span>
                            </label>
                            <input class="form-control" autocomplete="off" name="PhoneNumber" id="txt_phone" type="tel" maxlength="12" value="+47 912 34 567">
                        </div>
                        <div class="col-sm-12 col-md-6 col-lg-2 form-group">
                            <label for="txt_zip" class="required-field">
                                <span>Postnr</span>
                            </label>
                            <input class="form-control" name="ZipCode" id="txt_zip" autocomplete="off" type="text" maxlength="4" value="5700">
                        </div>
                    </div>
                    
                    <!-- Consent options with Ja/Nei radio buttons -->
                    <div class="row p-1">
                        <div class="col-sm-12 mb-2 d-flex flex-column flex-md-row align-middle">
                            <div class="btn-group btn-group-toggle mr-md-3 mb-1" data-toggle="buttons">
                                <label class="btn btn-sm btn-outline-primary">
                                    <input type="radio" name="rblKeepMeInformed" autocomplete="off" value="true">
                                    Ja
                                </label>
                                <label class="btn btn-sm btn-outline-primary active">
                                    <input type="radio" name="rblKeepMeInformed" autocomplete="off" value="false" checked>
                                    Nei
                                </label>
                            </div>
                            <span>Jeg ønsker bli informert om bud på eiendommen</span>
                        </div>
                    </div>
                    
                    <!-- Newsletter - hidden per Proaktiv config -->
                    <div class="row p-1" style="display: none;">
                        <div class="col-sm-12 mb-2 d-flex flex-column flex-md-row align-middle">
                            <div class="btn-group btn-group-toggle mr-md-3 mb-1" data-toggle="buttons">
                                <label class="btn btn-sm btn-outline-primary">
                                    <input type="radio" name="rbWantsCommercialNo" autocomplete="off" value="true">
                                    Ja
                                </label>
                                <label class="btn btn-sm btn-outline-primary active">
                                    <input type="radio" name="rbWantsCommercialNo" autocomplete="off" value="false" checked>
                                    Nei
                                </label>
                            </div>
                            <span>Jeg ønsker å abonnere på nyhetsbrev</span>
                        </div>
                    </div>
                    
                    <!-- Financing - only shown for Voss office -->
                    ${
                      showFinancing
                        ? `
                    <div class="row p-1">
                        <div class="col-sm-12 mb-2 d-flex flex-column flex-md-row align-middle">
                            <div class="btn-group btn-group-toggle mr-md-3 mb-1" data-toggle="buttons">
                                <label class="btn btn-sm btn-outline-primary">
                                    <input type="radio" name="rblConsentsContactForFinance" autocomplete="off" value="true">
                                    Ja
                                </label>
                                <label class="btn btn-sm btn-outline-primary active">
                                    <input type="radio" name="rblConsentsContactForFinance" autocomplete="off" value="false" checked>
                                    Nei
                                </label>
                            </div>
                            <span>Jeg ønsker tilbud om finansiering</span>
                        </div>
                    </div>
                    `
                        : ""
                    }
                    
                    <!-- Verdivurdering -->
                    <div class="row p-1">
                        <div class="col-sm-12 mb-2 d-flex flex-column flex-md-row align-middle">
                            <div class="btn-group btn-group-toggle mr-md-3 mb-1" data-toggle="buttons">
                                <label class="btn btn-sm btn-outline-primary">
                                    <input type="radio" name="rblConsentsContactForOwnEstate" autocomplete="off" value="true">
                                    Ja
                                </label>
                                <label class="btn btn-sm btn-outline-primary active">
                                    <input type="radio" name="rblConsentsContactForOwnEstate" autocomplete="off" value="false" checked>
                                    Nei
                                </label>
                            </div>
                            <span>Jeg ønsker verdivurdering av min bolig</span>
                        </div>
                    </div>
                </div>
            </fieldset>
        </div>
    </div>
    
    <!-- GDPR disclaimer and buttons -->
    <div class="row">
        <div class="col-sm-12 col-md-12 col-lg-7 form-group">
            <small>
                <span>Ved å sende inn skjemaet med navn og mobiltelefon aksepterer jeg at mine opplysninger lagres hos meglerforetaket og at jeg vil motta relevant informasjon om eiendommen.</span>
                <a class="consent-link" data-toggle="modal" data-target="#modal1" href="#">
                    <span class="link-text">Les mer</span> <i aria-hidden="true" class="far fa-question-circle"></i>
                </a>
            </small>
        </div>
        <div class="col-sm-12 col-md-12 col-lg-5 text-right">
            <button class="btn btn-primary btn-lg">Nullstill</button>
            <button class="btn btn-primary btn-lg" id="saveContact" name="action">Send salgsoppgave</button>
        </div>
    </div>
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
  // Proaktiv skin uses the custom branded CSS (same as Visningsportal)
  const skinCssHref = useVanillaSkin
    ? undefined
    : "/skins/proaktiv-visning.css";

  return (
    <PortalFrame
      content={mockupHtml}
      skinCssHref={skinCssHref}
      title={
        useVanillaSkin
          ? "Bestill salgsoppgave - Vanilla"
          : "Bestill salgsoppgave - Proaktiv"
      }
      minHeight={fullscreen ? "100vh" : "800px"}
      portalType="visning"
    />
  );
}
