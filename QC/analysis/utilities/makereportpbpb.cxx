#include <TStyle.h>

void histo_hestetics(TH1* h, int col, int marker);
void canvas_hestetics_single(TCanvas* c);
void canvas_hestetics_layout(TCanvas* c, int n = 3, int n1 = 0);
void canvas_multiple(TCanvas *c, int n);

void makereportpbpb(TString period = "LHC23g", TString pass = "apass1")
{

    gStyle->SetOptFit();
    // Get runlist
    system(Form("awk \'{print $1}\' jiratext.txt > listofruns"));
    std::vector<TString> run;
    FILE *file = fopen("listofruns","r");
    char *line;
    size_t len=0;
    while(getline(&line, &len, file) != -1) {
        run.push_back(line);
        run.back().Remove(run.back().Length() - 1);
    }
    fclose(file);

    //MO to check
    TString name[] = {
        "HitMap",
        "mEffPt_ITSTPC-ITSTPCTRD",
        "mEffPt_TPC",
        "mEffPt_TPCTRD",
        "mTOFChi2ITSTPC-ITSTPCTRD",
        "mTOFChi2TPC",
        "mTOFChi2TPCTRD",
        "DecodingErrors",
        "OrbitVsCrate",
        "DTimeTrk_sec09",
        "DeltaEvTimeTOFVsFT0ACSameBC",
        "EvTimeTOF",
        "DeltaBCTOFFT0",
        "BetavsP_ITSTPC_t0FT0AC",
        "BetavsP_ITSTPC_t0TOF",
        "mDeltaXEtaITSTPC-ITSTPCTRD",
        "mDeltaZEtaITSTPC-ITSTPCTRD"};

    const int n = sizeof(name)/sizeof(TString);
    const int nruns = run.size();

    // Color you life
    int col[] = {kRed, kBlue, kGreen, kOrange, kMagenta, kCyan, kBlack, kGray, kViolet, kTeal+2, kYellow, kMagenta,
                 kRed, kBlue, kGreen, kOrange, kMagenta, kCyan, kBlack, kGray, kViolet, kTeal+2, kYellow, kMagenta,
                 kRed, kBlue, kGreen, kOrange, kMagenta, kCyan, kBlack, kGray, kViolet, kTeal+2, kYellow, kMagenta,
                 kRed, kBlue, kGreen, kOrange, kMagenta, kCyan, kBlack, kGray, kViolet, kTeal+2, kYellow, kMagenta};
    int marker[] = {20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20,
                    24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24,
                    34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34,
                    28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28};
    const int ncol = sizeof(col) / sizeof(int);

    TLatex *label = new TLatex();
    label->SetTextFont(42);
    label->SetNDC();
    label->SetTextSize(0.05);
    label->SetTextAlign(22);
    label->SetTextAngle(0);

    TLatex *tinylabel = new TLatex();
    tinylabel->SetTextFont(42);
    tinylabel->SetNDC();
    tinylabel->SetTextSize(0.035);
    tinylabel->SetTextAlign(22);
    tinylabel->SetTextAngle(0);

    TH1D *pt = new TH1D("pt", ";p_{T} (GeV/c);Matching efficiency;", 10, 0., 20.);
    TH1D *ptcorr = new TH1D("ptcorr", ";p_{T} (GeV/c);Matching efficiency (corrected for acceptance);", 10, 0., 10.);
    TH1D *etaz = new TH1D("eta", ";#eta; #Delta z (cm);", 10, -1, +1);
    TH1D *chi = new TH1D("chi", ";#chi^{2} (cm);Counts (normalized);", 10, 0, +10);
    pt->SetStats(0);
    ptcorr->SetStats(0);
    etaz->SetStats(0);
    chi->SetStats(0);
    pt->GetYaxis()->SetRangeUser(0., 1.1);
    ptcorr->GetYaxis()->SetRangeUser(0., 1.1);
    etaz->GetYaxis()->SetRangeUser(-10., 10.);
    chi->GetYaxis()->SetRangeUser(0., 0.1);

    // Open files and get MOs
    TFile* f[n][nruns];
    TH2F* hHitMap[nruns];
    TEfficiency* hEff[3][nruns];
    TH1D* hChi2[3][nruns];
    TH2D *hDecodingE[nruns];
    TH2D *hOrbitVsCrate[nruns];
    TH1D * hTrkTime[nruns];
    TH1D* hDeltaFT0TOF[nruns];
    TH1D* ht0TOF[nruns];
    TH1D* hDeltaBCT0TOF[nruns];
    TH2D *hBetavsP_ITSTPC_t0FT0AC[nruns];
    TH2D *hBetavsP_ITSTPC_t0TOF[nruns];
    TH2D* hDeltaXEtaITSTPC[nruns];
    TH2D* hDeltaZEtaITSTPC[nruns];

    for (int n_run = 0; n_run < nruns; n_run++)
    {
        for (int i_obj = 0; i_obj < n; i_obj++)
        {
            f[i_obj][n_run] = TFile::Open(Form("Run%s/rootfiles/%s.root",  run.at(n_run).Data(), name[i_obj].Data()));
        }

        hHitMap[n_run] = (TH2F *)f[0][n_run]->Get("ccdb_object");

        hEff[0][n_run] = (TEfficiency *)f[1][n_run]->Get("ccdb_object");
        hEff[1][n_run] = (TEfficiency *)f[2][n_run]->Get("ccdb_object");
        hEff[2][n_run] = (TEfficiency *)f[3][n_run]->Get("ccdb_object");

        hChi2[0][n_run] = (TH1D *)f[4][n_run]->Get("ccdb_object");
        hChi2[1][n_run] = (TH1D *)f[5][n_run]->Get("ccdb_object");
        hChi2[2][n_run] = (TH1D *)f[6][n_run]->Get("ccdb_object");

        hDecodingE[n_run] = (TH2D *)f[7][n_run]->Get("ccdb_object");

        hOrbitVsCrate[n_run] = (TH2D *)f[8][n_run]->Get("ccdb_object");

        hTrkTime[n_run] = (TH1D *)f[9][n_run]->Get("ccdb_object");

        hDeltaFT0TOF[n_run] = (TH1D *)f[10][n_run]->Get("ccdb_object");

        ht0TOF[n_run] = (TH1D *)f[11][n_run]->Get("ccdb_object");

        hDeltaBCT0TOF[n_run] = (TH1D *)f[12][n_run]->Get("ccdb_object");

        hBetavsP_ITSTPC_t0FT0AC[n_run] = (TH2D *)f[13][n_run]->Get("ccdb_object");
        hBetavsP_ITSTPC_t0TOF[n_run] = (TH2D *)f[14][n_run]->Get("ccdb_object");

        hDeltaXEtaITSTPC[n_run] = (TH2D *)f[15][n_run]->Get("ccdb_object");
        hDeltaZEtaITSTPC[n_run] = (TH2D *)f[16][n_run]->Get("ccdb_object");

        histo_hestetics(hChi2[0][n_run], col[n_run], marker[n_run]);
        histo_hestetics(hChi2[1][n_run], col[n_run], marker[n_run]);
        histo_hestetics(hChi2[2][n_run], col[n_run], marker[n_run]);
        histo_hestetics(hDeltaBCT0TOF[n_run], col[n_run], marker[n_run]);
    }

    TLegend *leg = new TLegend(0.23, 0.7, 0.8, 0.88);
    leg->SetBorderSize(0);
    leg->SetFillStyle(0);
    leg->SetTextFont(42);
    leg->SetTextSize(0.03);
    leg->SetNColumns(3);
    for (int i = 0; i < nruns; i++){
        leg->AddEntry(hEff[0][i], Form("%s", run.at(i).Data()), "LEP");
    }

    ///////////////////////////
    ///////// HIT MAP /////////
    ///////////////////////////

    TCanvas* chitmap[nruns];
    TCanvas* chitmap_summary = new TCanvas(Form("chitmap_summary"), "", 1200, 1000);
    canvas_multiple(chitmap_summary, nruns);

    int countchannels[nruns];

    //PHOS hole
    int minx = hHitMap[0]->GetXaxis()->FindBin(13);
    int maxx = hHitMap[0]->GetXaxis()->FindBin(16);
    int miny = hHitMap[0]->GetYaxis()->FindBin(38);
    int maxy = hHitMap[0]->GetYaxis()->FindBin(52);

    int totch = (hHitMap[0]->GetNbinsX() * hHitMap[0]->GetNbinsY());
    /* - (maxx-minx)*(maxy-miny); //PHOS hole
    cout << "Tot av. channels: " << totch << " = all ("
         << (hHitMap[0]->GetNbinsX() * hHitMap[0]->GetNbinsY()) <<
         ") - PHOS hole (" << (maxx - minx) * (maxy - miny) << ")" << endl;
    */
    TH1D* hProjY[nruns];
    double deccorr[nruns];
    for (int i = 0; i < nruns; i++){
        countchannels[i] = 0;

        chitmap[i] = new TCanvas(Form("chitmap_%s", run.at(i).Data()), "", 1000, 900);
        canvas_hestetics_single(chitmap[i]);
        chitmap[i]->SetLogz();
        hHitMap[i]->Draw("colz");
        hHitMap[i]->SetTitle("");

        for (int isect = 1; isect <= hHitMap[i]->GetNbinsX(); isect++){
            for (int istrip = 1; istrip <= hHitMap[i]->GetNbinsY(); istrip++){

                if (hHitMap[i]->GetBinContent(isect, istrip) > 1000) countchannels[i]++;
            }
        }
        cout << "Frac active channels: " << countchannels[i]/totch << endl;

        tinylabel->DrawLatex(0.35, 0.85, Form("active channels: %.1f %s", (double)countchannels[i] / totch * 100, "%"));
        label->DrawLatex(0.75, 0.95, Form("Run %s", run.at(i).Data()));
        label->DrawLatex(0.3, 0.95, Form("%s %s", period.Data(), pass.Data()));
        chitmap[i]->SaveAs(Form("images/HitMap_%s.png", run.at(i).Data()));
        chitmap[i]->SaveAs(Form("Summary_Run%s_%s_%s.pdf(", run.at(i).Data(), period.Data(), pass.Data()));

        //Projection for Decoding Errors
        hProjY[i] = (TH1D*)hDecodingE[i]->ProjectionY();
        hProjY[i]->Scale(1./hProjY[i]->GetBinContent(1));
        for (int ibin = 3; ibin < hProjY[i]->GetNbinsX(); ibin++){
            deccorr[i] += hProjY[i]->GetBinContent(ibin);
        }
        deccorr[i] /= 10;

        chitmap_summary->cd(i+1);
        hHitMap[i]->Draw("colz");
        label->DrawLatex(0.75, 0.95, Form("Run %s", run.at(i).Data()));
        tinylabel->DrawLatex(0.35, 0.85, Form("active channels: %.1f %s", (double)countchannels[i] / totch * 100, "%"));
    }

    chitmap_summary->SaveAs(Form("Summary_%s_%s.pdf(", period.Data(), pass.Data()));

    ///////////////////////////////////
    ///////// DECODING ERRORS /////////
    ///////////////////////////////////

    TCanvas* cdec[nruns];
    TLine* l[nruns];
    TLegend* legdec[nruns];
    for (int i = 0; i < nruns; i++){
        cdec[i] = new TCanvas(Form("cdec%i",i), "", 1000, 900);
        canvas_hestetics_single(cdec[i]);
        legdec[i] = new TLegend(0.29, 0.82, 0.6, 0.88);
        legdec[i]->SetBorderSize(0);
        legdec[i]->SetTextFont(42);
        legdec[i]->SetTextSize(0.03);
        hProjY[i]->GetXaxis()->SetRangeUser(3.5, 12.5);
        hProjY[i]->GetXaxis()->SetTitle("");
        hProjY[i]->GetYaxis()->SetTitle("Errors %");
        hProjY[i]->GetYaxis()->SetRangeUser(0., 1);
        hProjY[i]->SetLineWidth(2);
        hProjY[i]->SetTitle("");
        hProjY[i]->SetStats(0);
        hProjY[i]->SetMarkerStyle(20);
        hProjY[i]->Draw();
        l[i] = new TLine(3., deccorr[i], 13., deccorr[i]);
        l[i]->SetLineColor(kRed);
        l[i]->SetLineStyle(7);
        l[i]->Draw("SAME");
        legdec[i]->AddEntry(l[i], Form("Average TRM inefficiency: %.1f %s", (double)deccorr[i]*100, "%"), "L");
        legdec[i]->Draw("SAME");
        //tinylabel->DrawLatex(0.39, 0.84, Form("Average TRM inefficiency: %.1f %s", (double)deccorr[i]*100, "%"));
        label->DrawLatex(0.3, 0.95, Form("%s %s", period.Data(), pass.Data()));
        label->DrawLatex(0.75, 0.95, Form("Run %s", run.at(i).Data()));

        cdec[i]->SaveAs(Form("images/DecodingErrors_%s.png", run.at(i).Data()));
        cdec[i]->SaveAs(Form("Summary_Run%s_%s_%s.pdf", run.at(i).Data(), period.Data(), pass.Data()));
    }

    //////////////////////////////
    ///////// DRM ERRORS /////////
    //////////////////////////////

    TCanvas* corbit[nruns];
    TH2D* hOrbitVsCrateClone[nruns];
    double drmcorr[nruns];
    for (int i = 0; i < nruns; i++){
        corbit[i] = new TCanvas(Form("corbit%i",i), "", 1000, 900);
        canvas_hestetics_single(corbit[i]);
        hOrbitVsCrate[i]->SetTitle("");
        hOrbitVsCrate[i]->SetStats(0);
        hOrbitVsCrate[i]->GetYaxis()->SetRangeUser(0,150);
        hOrbitVsCrate[i]->Draw("colz");
        label->DrawLatex(0.3, 0.95, Form("%s %s", period.Data(), pass.Data()));
        label->DrawLatex(0.75, 0.95, Form("Run %s", run.at(i).Data()));

        hOrbitVsCrateClone[i] = (TH2D*)hOrbitVsCrate[i]->Clone();
        hOrbitVsCrateClone[i]->Divide(hOrbitVsCrate[i]);

        drmcorr[i] = hOrbitVsCrate[i]->Integral()/ hOrbitVsCrateClone[i]->Integral();

        tinylabel->DrawLatex(0.4, 0.85, Form("Average DRM efficiency: %.1f %s", (double)drmcorr[i]*100, "%"));
        corbit[i]->SaveAs(Form("images/OrbitVsCrate_%s.png", run.at(i).Data()));
        corbit[i]->SaveAs(Form("Summary_Run%s_%s_%s.pdf", run.at(i).Data(), period.Data(), pass.Data()));
    }

    ///////////////////////////////////
    ///////// MATCH EFFICIENCY ////////
    ///////////////////////////////////

    TCanvas* ceff[3];
    TString tracktypebis[3] = {"ITSTPC-ITSTPCTRD", "TPC", "TPCTRD"};
    for (int itracktype = 0; itracktype < 3; itracktype++) {
        ceff[itracktype] = new TCanvas(Form("ceff_%s", tracktypebis[itracktype].Data()), "", 1000, 900);
        canvas_hestetics_single(ceff[itracktype]);
        pt->Draw();
        for (int i = 0; i < nruns; i++) {
            hEff[0 + itracktype][i]->Draw("SAME EP");
            hEff[0 + itracktype][i]->SetLineColor(col[i]);
            hEff[0 + itracktype][i]->SetMarkerColor(col[i]);
            hEff[0 + itracktype][i]->SetMarkerStyle(marker[i]);
        }
        leg->Draw();
        label->DrawLatex(0.75, 0.95, Form("%s", tracktypebis[itracktype].Data()));
        label->DrawLatex(0.3, 0.95, Form("%s %s", period.Data(),pass.Data()));
        ceff[itracktype]->SaveAs(Form("images/EffPt%s.png", tracktypebis[itracktype].Data()));
    }

    /////////////////////////////////////////////
    ///////// MATCH EFFICIENCY CORRECTED ////////
    /////////////////////////////////////////////

    TCanvas* ceffcorr[3];
    TH1F* hEffCorr[3][nruns];
    int neffbins = hEff[0][0]->GetTotalHistogram()->GetNbinsX();
    for (int itracktype = 0; itracktype < 3; itracktype++) {
        ceffcorr[itracktype] = new TCanvas(Form("ceffcorr_%s", tracktypebis[itracktype].Data()), "", 1000, 900);
        canvas_hestetics_single(ceffcorr[itracktype]);
        ptcorr->Draw();
        for (int i = 0; i < nruns; i++) {
            hEffCorr[0 + itracktype][i] = new TH1F(Form("hEffCorr_%s_%s", tracktypebis[itracktype].Data(), run.at(i).Data()), "", neffbins, 0., 20);
            for (int ibin = 1; ibin <= neffbins; ibin++){
                hEffCorr[0 + itracktype][i]->SetBinContent(ibin, hEff[0 + itracktype][i]->GetEfficiency(ibin));
                hEffCorr[0 + itracktype][i]->SetBinError(ibin, hEff[0 + itracktype][i]->GetEfficiencyErrorUp(ibin));
            }
            hEffCorr[0 + itracktype][i]->Scale(1. / ((double)countchannels[i] / totch));
            hEffCorr[0 + itracktype][i]->Scale(1. / (1-deccorr[i]));
            hEffCorr[0 + itracktype][i]->Scale(1. / drmcorr[i]);
            hEffCorr[0 + itracktype][i]->Draw("SAME EP");
            histo_hestetics(hEffCorr[0 + itracktype][i], col[i], marker[i]);
        }
        leg->Draw();
        label->DrawLatex(0.3, 0.95, Form("%s %s", period.Data(), pass.Data()));
        label->DrawLatex(0.75, 0.95, Form("%s", tracktypebis[itracktype].Data()));
        ceffcorr[itracktype]->SaveAs(Form("images/CorrEffPt%s.png", tracktypebis[itracktype].Data()));
    }

    ceffcorr[0]->SaveAs(Form("Summary_%s_%s.pdf", period.Data(),pass.Data()));

    TCanvas *ceffcorr_runs[3][nruns];
    for (int itracktype = 0; itracktype < 3; itracktype++) {
        for (int i = 0; i < nruns; i++) {
            ceffcorr_runs[itracktype][i] = new TCanvas(Form("ceffcorr_runs_%s", tracktypebis[itracktype].Data()), "", 1000, 900);
            canvas_hestetics_single(ceffcorr_runs[itracktype][i]);
            ptcorr->Draw();
            hEffCorr[0 + itracktype][i]->Draw("SAME EP");
            label->DrawLatex(0.3, 0.95, Form("%s %s", period.Data(), pass.Data()));
            label->DrawLatex(0.75, 0.95, Form("Run %s", run.at(i).Data()));
            label->DrawLatex(0.6, 0.85, Form("%s", tracktypebis[itracktype].Data()));
            ceffcorr_runs[0 + itracktype][i]->SaveAs(Form("Summary_Run%s_%s_%s.pdf", run.at(i).Data(), period.Data(), pass.Data()));
        }
    }

    TH1F* htrendEff[3];
    TH1F *htrendCorr_tot[3];
    TH1F *htrendCorr_ch[3];
    TH1F *htrendCorr_trm[3];
    TH1F *htrendCorr_drm[3];

    TCanvas *ctrendcorr[3];
    TCanvas *ctrendacccorr[3];
    for (int itracktype = 0; itracktype < 3; itracktype++) {
        ctrendcorr[itracktype] = new TCanvas(Form("ctrendcorr_%s", tracktypebis[itracktype].Data()), "", 1800, 1000);
        canvas_hestetics_single(ctrendcorr[itracktype]);


        htrendEff[itracktype] = new TH1F(Form("htrendEff_%s", tracktypebis[itracktype].Data()), ";;Matching efficiency (p_{T} = 2.5 GeV/c))", nruns, 0., nruns);
        htrendCorr_ch[itracktype] = new TH1F(Form("htrendCorr_tot_%s", tracktypebis[itracktype].Data()), ";;Correction", nruns, 0., nruns);
        htrendCorr_trm[itracktype] = new TH1F(Form("htrendCorr_ch_%s", tracktypebis[itracktype].Data()), ";;Corr for decoding errors", nruns, 0., nruns);
        htrendCorr_drm[itracktype] = new TH1F(Form("htrendCorr_trm_%s", tracktypebis[itracktype].Data()), ";;Corr for lost orbits", nruns, 0., nruns);
        htrendCorr_tot[itracktype] = new TH1F(Form("htrendCorr_drm_%s", tracktypebis[itracktype].Data()), ";;Corr TOT", nruns, 0., nruns);

        for (int i = 0; i < nruns; i++) {
            htrendEff[itracktype]->GetXaxis()->SetBinLabel(i + 1, run.at(i).Data());
            htrendEff[itracktype]->SetBinContent(i + 1, hEffCorr[0 + itracktype][i]->GetBinContent(hEffCorr[0 + itracktype][i]->FindBin(2.5)));
            htrendEff[itracktype]->SetBinError(i + 1, hEffCorr[0 + itracktype][i]->GetBinError(hEffCorr[0 + itracktype][i]->FindBin(2.5)));

            htrendCorr_ch[itracktype]->GetXaxis()->SetBinLabel(i + 1, run.at(i).Data());
            htrendCorr_ch[itracktype]->SetBinContent(i + 1, ((double)countchannels[i] / totch));
            htrendCorr_ch[itracktype]->SetBinError(i + 1, 0);

            htrendCorr_trm[itracktype]->GetXaxis()->SetBinLabel(i + 1, run.at(i).Data());
            htrendCorr_trm[itracktype]->SetBinContent(i + 1, (1-deccorr[i]));
            htrendCorr_trm[itracktype]->SetBinError(i + 1, 0);

            htrendCorr_drm[itracktype]->GetXaxis()->SetBinLabel(i + 1, run.at(i).Data());
            htrendCorr_drm[itracktype]->SetBinContent(i + 1, drmcorr[i]);
            htrendCorr_drm[itracktype]->SetBinError(i + 1, 0);

            htrendCorr_tot[itracktype]->GetXaxis()->SetBinLabel(i + 1, run.at(i).Data());
            htrendCorr_tot[itracktype]->SetBinContent(i + 1, ((double)countchannels[i] / totch) * (1-deccorr[i]) * drmcorr[i]);
            htrendCorr_tot[itracktype]->SetBinError(i + 1, 0);
        }
        htrendEff[itracktype]->SetStats(0);
        htrendEff[itracktype]->GetYaxis()->SetRangeUser(0., 1.1);
        htrendEff[itracktype]->SetLineColor(kBlack);
        htrendEff[itracktype]->SetLineWidth(2);
        htrendEff[itracktype]->SetMarkerColor(kBlack);
        htrendEff[itracktype]->SetMarkerStyle(20);
        htrendEff[itracktype]->Draw("EP");

        TLine *linemc = new TLine(0., 0.65, nruns, 0.65);
        linemc->SetLineColor(kRed);
        linemc->SetLineWidth(1);
        linemc->SetLineStyle(1);
        linemc->Draw("SAME");

        htrendEff[itracktype]->Draw("SAME EP");

        label->DrawLatex(0.75, 0.95, Form("%s", tracktypebis[itracktype].Data()));
        label->DrawLatex(0.3, 0.95, Form("%s %s", period.Data(), pass.Data()));

        ctrendcorr[itracktype]->SaveAs(Form("images/TrendCorrEffPt%s.png", tracktypebis[itracktype].Data()));
    }
    ctrendcorr[0]->SaveAs(Form("Summary_%s_%s.pdf", period.Data(),pass.Data()));

    //Corrections
    TLegend *legcorr = new TLegend(0.23, 0.7, 0.8, 0.88);
    legcorr->SetBorderSize(0);
    legcorr->SetFillStyle(0);
    legcorr->SetTextFont(42);
    legcorr->SetTextSize(0.03);
    for (int itracktype = 0; itracktype < 3; itracktype++) {
        ctrendacccorr[itracktype] = new TCanvas(Form("ctrendacccorr_%s", tracktypebis[itracktype].Data()), "", 1800, 1000);
        canvas_hestetics_single(ctrendacccorr[itracktype]);
        htrendCorr_ch[itracktype]->SetStats(0);
        htrendCorr_ch[itracktype]->GetYaxis()->SetRangeUser(0.8, 1.1);
        htrendCorr_ch[itracktype]->SetLineColor(kRed);
        htrendCorr_ch[itracktype]->SetLineWidth(2);
        htrendCorr_ch[itracktype]->SetMarkerColor(kRed);
        htrendCorr_ch[itracktype]->SetMarkerStyle(20);
        htrendCorr_ch[itracktype]->Draw("HIST");
        htrendCorr_trm[itracktype]->SetStats(0);
        htrendCorr_trm[itracktype]->GetYaxis()->SetRangeUser(0., 1.1);
        htrendCorr_trm[itracktype]->SetLineColor(kGreen+1);
        htrendCorr_trm[itracktype]->SetLineWidth(2);
        htrendCorr_trm[itracktype]->SetMarkerColor(kGreen+1);
        htrendCorr_trm[itracktype]->SetMarkerStyle(20);
        htrendCorr_trm[itracktype]->Draw("HIST SAME");
        htrendCorr_drm[itracktype]->SetStats(0);
        htrendCorr_drm[itracktype]->GetYaxis()->SetRangeUser(0., 1.1);
        htrendCorr_drm[itracktype]->SetLineColor(kBlue);
        htrendCorr_drm[itracktype]->SetLineWidth(2);
        htrendCorr_drm[itracktype]->SetMarkerColor(kBlue);
        htrendCorr_drm[itracktype]->SetMarkerStyle(20);
        htrendCorr_drm[itracktype]->Draw("HIST SAME");
        htrendCorr_tot[itracktype]->SetStats(0);
        htrendCorr_tot[itracktype]->GetYaxis()->SetRangeUser(0., 1.1);
        htrendCorr_tot[itracktype]->SetLineColor(kBlack);
        htrendCorr_tot[itracktype]->SetLineWidth(2);
        htrendCorr_tot[itracktype]->SetMarkerColor(kBlack);
        htrendCorr_tot[itracktype]->SetMarkerStyle(20);
        htrendCorr_tot[itracktype]->Draw("HIST SAME");

        if (itracktype==0){
            legcorr->AddEntry(htrendCorr_ch[itracktype], "Active channels", "L");
            legcorr->AddEntry(htrendCorr_trm[itracktype], "Decoding errors", "L");
            legcorr->AddEntry(htrendCorr_drm[itracktype], "Lost orbits", "L");
            legcorr->AddEntry(htrendCorr_tot[itracktype], "Total", "L");
        }
        legcorr->Draw();
        label->DrawLatex(0.75, 0.95, Form("%s", tracktypebis[itracktype].Data()));
        label->DrawLatex(0.3, 0.95, Form("%s %s", period.Data(), pass.Data()));

        ctrendacccorr[itracktype]->SaveAs(Form("images/TrendAccCorr%s.png", tracktypebis[itracktype].Data()));
    }

    ctrendacccorr[0]->SaveAs(Form("Summary_%s_%s.pdf", period.Data(), pass.Data()));

    ///////////////////////////////////
    //////////// TOF CHI2 /////////////
    ///////////////////////////////////

    TCanvas* cchi[3];
    for (int itracktype = 0; itracktype < 3; itracktype++) {
        cchi[itracktype] = new TCanvas(Form("cchi_%s", tracktypebis[itracktype].Data()), "", 1000, 900);
        canvas_hestetics_single(cchi[itracktype]);
        chi->Draw();
        for (int i = 0; i < nruns; i++) {
            hChi2[0 + itracktype][i]->DrawNormalized("SAME EP");
            hChi2[0 + itracktype][i]->SetLineColor(col[i]);
            hChi2[0 + itracktype][i]->SetMarkerColor(col[i]);
            hChi2[0 + itracktype][i]->SetMarkerStyle(marker[i]);
        }
        leg->Draw();
        label->DrawLatex(0.75, 0.95, Form("%s", tracktypebis[itracktype].Data()));
        label->DrawLatex(0.3, 0.95, Form("%s %s", period.Data(), pass.Data()));
        cchi[itracktype]->SaveAs(Form("images/Chi2%s.png", tracktypebis[itracktype].Data()));
   }
   cchi[0]->SaveAs(Form("Summary_%s_%s.pdf", period.Data(),pass.Data()));

    TCanvas *cchi_runs[3][nruns];
    for (int itracktype = 0; itracktype < 3; itracktype++) {
        for (int i = 0; i < nruns; i++) {
            cchi_runs[itracktype][i] = new TCanvas(Form("cchi_runs_%s", tracktypebis[itracktype].Data()), "", 1000, 900);
            canvas_hestetics_single(cchi_runs[itracktype][i]);
            chi->Draw();
            hChi2[0 + itracktype][i]->DrawNormalized("SAME EP");
            label->DrawLatex(0.3, 0.95, Form("%s %s", period.Data(), pass.Data()));
            label->DrawLatex(0.75, 0.95, Form("Run %s", run.at(i).Data()));
            label->DrawLatex(0.6, 0.85, Form("%s", tracktypebis[itracktype].Data()));
            cchi_runs[0 + itracktype][i]->SaveAs(Form("Summary_Run%s_%s_%s.pdf", run.at(i).Data(), period.Data(), pass.Data()));
        }
    }

    ///////////////////////////////////
    //////////// RESIDUALS ////////////
    ///////////////////////////////////

    TCanvas *cresz[nruns];
    TCanvas *cresz_summary = new TCanvas("cresz_summary", "", 1000, 1000);
    canvas_hestetics_single(cresz_summary);
    TProfile *hProjX_ResZ[nruns];
    for (int i = 0; i < nruns; i++)
    {
        cresz[i] = new TCanvas(Form("cresz_%s", run.at(i).Data()), "", 1000, 900);
        canvas_hestetics_single(cresz[i]);
        cresz[i]->SetLogz();
        hDeltaZEtaITSTPC[i]->SetStats(0);
        hDeltaZEtaITSTPC[i]->SetTitle("Residuals z (cm), ITS-TPC(-TRD) tracks");
        hDeltaZEtaITSTPC[i]->Draw("colz");

        cresz[i]->SaveAs(Form("images/resz_%s.png", run.at(i).Data()));
        cresz[i]->SaveAs(Form("Summary_Run%s_%s_%s.pdf", run.at(i).Data(), period.Data(), pass.Data()));

        hProjX_ResZ[i] = hDeltaZEtaITSTPC[i]->ProfileX(Form("pz_%s", run.at(i).Data()));
        histo_hestetics(hProjX_ResZ[i], col[i], marker[i]);
        cresz_summary->cd();
        hProjX_ResZ[i]->GetYaxis()->SetTitle("#Delta z (cm)");
        hProjX_ResZ[i]->GetYaxis()->SetLabelSize(0.04);
        hProjX_ResZ[i]->GetXaxis()->SetLabelSize(0.04);
        hProjX_ResZ[i]->GetYaxis()->SetRangeUser(-10,10);
        hProjX_ResZ[i]->Draw("SAME EP");
    }
    leg->Draw();
    cresz_summary->SaveAs(Form("Summary_%s_%s.pdf", period.Data(),pass.Data()));

    TCanvas *cresx[nruns];
    TCanvas *cresx_summary = new TCanvas("cresx_summary", "", 1000, 1000);
    canvas_hestetics_single(cresx_summary);
    TProfile *hProjX_Resx[nruns];
    for (int i = 0; i < nruns; i++)
    {
        cresx[i] = new TCanvas(Form("cresx_%s", run.at(i).Data()), "", 1000, 900);
        canvas_hestetics_single(cresx[i]);
        cresx[i]->SetLogz();
        hDeltaXEtaITSTPC[i]->SetStats(0);
        hDeltaXEtaITSTPC[i]->SetTitle("Residuals x (cm), ITS-TPC(-TRD) tracks");
        hDeltaXEtaITSTPC[i]->Draw("colz");

        cresx[i]->SaveAs(Form("images/resx_%s.png", run.at(i).Data()));
        cresx[i]->SaveAs(Form("Summary_Run%s_%s_%s.pdf", run.at(i).Data(), period.Data(), pass.Data()));

        hProjX_Resx[i] = hDeltaXEtaITSTPC[i]->ProfileX(Form("px_%s", run.at(i).Data()));
        histo_hestetics(hProjX_Resx[i], col[i], marker[i]);
        cresx_summary->cd();
        hProjX_Resx[i]->GetYaxis()->SetTitle("#Delta x (cm)");
        hProjX_Resx[i]->GetYaxis()->SetLabelSize(0.04);
        hProjX_Resx[i]->GetXaxis()->SetLabelSize(0.04);
        hProjX_Resx[i]->GetYaxis()->SetRangeUser(-10, 10);
        hProjX_Resx[i]->Draw("SAME EP");
    }
    leg->Draw();
    cresx_summary->SaveAs(Form("Summary_%s_%s.pdf", period.Data(),pass.Data()));

    ///////////////////////////////////
    ///////////// TRACK-TIME //////////
    ///////////////////////////////////

    TCanvas *deltatbc[nruns];
    for (int i = 0; i < nruns; i++)
    {
        deltatbc[i] = new TCanvas(Form("deltatbc_%s", run.at(i).Data()), "", 1000, 800);
        canvas_hestetics_single(deltatbc[i]);
        deltatbc[i]->SetLogz();
        hTrkTime[i]->SetStats(0);
        hTrkTime[i]->Draw("colz");
        label->DrawLatex(0.3, 0.85, Form("%s %s", period.Data(), pass.Data()));
        deltatbc[i]->SaveAs(Form("images/DeltattrackBCSec09_%s.png", run.at(i).Data()));
        deltatbc[i]->SaveAs(Form("Summary_Run%s_%s_%s.pdf", run.at(i).Data(), period.Data(), pass.Data()));
    }


    ///////////////////////////////////
    ///////////// FT0 - TOF ///////////
    ///////////////////////////////////

    TCanvas *cdeltaBC_tofft0[nruns];
    TCanvas *cdeltaBC_summary = new TCanvas(Form("cdeltaBC_summary"), "", 1000, 800);
    for (int i = 0; i < nruns; i++)
    {
        cdeltaBC_tofft0[i] = new TCanvas(Form("cdeltaBC_tofft0_%s", run.at(i).Data()), "", 1000, 800);
        cdeltaBC_tofft0[i]->SetBottomMargin(0.15);
        cdeltaBC_tofft0[i]->SetBottomMargin(0.15);
        hDeltaBCT0TOF[i]->SetStats(0);
        hDeltaBCT0TOF[i]->GetYaxis()->SetRangeUser(0, 4*hDeltaBCT0TOF[i]->GetMaximum());
        hDeltaBCT0TOF[i]->Draw("HIST P");
        hDeltaBCT0TOF[i]->Draw("HIST SAME");

        cdeltaBC_tofft0[i]->SaveAs(Form("Summary_Run%s_%s_%s.pdf", run.at(i).Data(), period.Data(), pass.Data()));

        cdeltaBC_summary->cd();
        hDeltaBCT0TOF[i]->Draw("HIST P");
        hDeltaBCT0TOF[i]->Draw("HIST SAME");
    }
    leg->Draw();
    cdeltaBC_summary->SaveAs(Form("Summary_%s_%s.pdf", period.Data(),pass.Data()));

    TCanvas *cdeltaevtime_tofft0[nruns];
    TF1 *gaus[nruns];
    Double_t MeanFT0TOF[nruns], MeanFT0TOFError[nruns];
    for (int i = 0; i < nruns; i++)
    {
        cdeltaevtime_tofft0[i] = new TCanvas(Form("cdeltaevtime_tofft0_%s", run.at(i).Data()), "", 1000, 800);
        gaus[i] = new TF1("gaus", "gaus", hDeltaFT0TOF[i]->GetMean() - hDeltaFT0TOF[i]->GetStdDev(), hDeltaFT0TOF[i]->GetMean() + hDeltaFT0TOF[i]->GetStdDev());

        cdeltaevtime_tofft0[i]->SetBottomMargin(0.15);
        cdeltaevtime_tofft0[i]->SetBottomMargin(0.15);

        hDeltaFT0TOF[i]->SetStats(0);
        hDeltaFT0TOF[i]->Draw("HIST");
        hDeltaFT0TOF[i]->GetXaxis()->SetRangeUser(-1500, 1500);
        hDeltaFT0TOF[i]->SetLineColor(kBlack);
        hDeltaFT0TOF[i]->Fit(gaus[i], "0Rq");
        hDeltaFT0TOF[i]->SetTitle("t_{0}^{TOF}-t_{0}^{FT0AC}");

        gaus[i]->Draw("SAME");

        MeanFT0TOF[i] = gaus[i]->GetParameter(1);
        MeanFT0TOFError[i] = gaus[i]->GetParError(1);

        label->DrawLatex(0.7, 0.85, Form("Mean %.1f", gaus[i]->GetParameter(1)));
        label->DrawLatex(0.7, 0.8, Form("Sigma %.1f", gaus[i]->GetParameter(2)));
        //label->DrawLatex(0.7, 0.75, Form("Chi2/ndf %.1f", gaus[i]->GetChisquare() / gaus[i]->GetNDF()));
        label->DrawLatex(0.3, 0.85, Form("Run %s", run.at(i).Data()));

        cdeltaevtime_tofft0[i]->SaveAs(Form("images/Deltaevtimeft0_%s.png", run.at(i).Data()));
        cdeltaevtime_tofft0[i]->SaveAs(Form("Summary_Run%s_%s_%s.pdf", run.at(i).Data(), period.Data(), pass.Data()));
    }

    TCanvas *cevtimetof[nruns];
    Double_t Meant0TOF[nruns];
    Double_t Meant0TOFError[nruns];
    TF1 *gaus2[nruns];
    TH1D* ht0;
    for (int i = 0; i < nruns; i++)
    {
        cevtimetof[i] = new TCanvas(Form("cevtimetof_%s", run.at(i).Data()), "", 1000, 800);
        gaus2[i] = new TF1("gaus", "gaus", ht0TOF[i]->GetMean() - 2*ht0TOF[i]->GetStdDev(), ht0TOF[i]->GetMean() + 2*ht0TOF[i]->GetStdDev());

        cevtimetof[i]->SetBottomMargin(0.15);
        cevtimetof[i]->SetLeftMargin(0.15);

        for (int bin = 1; bin <= ht0TOF[i]->GetNbinsX(); bin++)
        {
            if (ht0TOF[i]->GetBinContent(bin) > 0.5 * ht0TOF[i]->GetMaximum())
            {
                ht0TOF[i]->SetBinContent(bin, (ht0TOF[i]->GetBinContent(bin - 1) + ht0TOF[i]->GetBinContent(bin + 1)) / 2);
            }
        }
        ht0TOF[i]->SetStats(0);
        ht0TOF[i]->Fit(gaus2[i], "0Rq");
        ht0TOF[i]->Draw("hist");
        ht0TOF[i]->GetXaxis()->SetRangeUser(-1000, 1000);

        gaus2[i]->Draw("SAME");

        Meant0TOF[i] = gaus2[i]->GetParameter(1);
        Meant0TOFError[i] = gaus2[i]->GetParError(1);

        label->DrawLatex(0.3, 0.85, Form("Run %s", run.at(i).Data()));
        label->DrawLatex(0.7, 0.85, Form("Mean %.1f", gaus2[i]->GetParameter(1)));
        label->DrawLatex(0.7, 0.8, Form("Sigma %.1f", gaus2[i]->GetParameter(2)));
        //label->DrawLatex(0.7, 0.75, Form("Chi2/ndf %.1f", gaus2[i]->GetChisquare() / gaus2[i]->GetNDF()));
        label->DrawLatex(0.3, 0.85, Form("Run %s", run.at(i).Data()));

        cevtimetof[i]->SaveAs(Form("images/Evtimetof_%s.png", run.at(i).Data()));
        cevtimetof[i]->SaveAs(Form("Summary_Run%s_%s_%s.pdf", run.at(i).Data(), period.Data(), pass.Data()));
    }

    TCanvas *trendFT0TOF = new TCanvas("trendFT0TOF", "", 1600, 800);
    trendFT0TOF->SetBottomMargin(0.15);
    trendFT0TOF->SetLeftMargin(0.15);
    trendFT0TOF->SetGridx();
    TH1F *grMeanFT0TOF = new TH1F("grMeanFT0TOF", "trending t0_{FT0}-t0_{TOF}", nruns, 0, nruns);
    grMeanFT0TOF->SetTitle("trending FT0-TOF");
    grMeanFT0TOF->GetYaxis()->SetTitle("#LT t_{FT0} - t_{TOF} #GT (ps)");
    for (int bin = 1; bin <= grMeanFT0TOF->GetNbinsX(); bin++)
    {
        grMeanFT0TOF->SetBinContent(bin, MeanFT0TOF[bin - 1]);
        grMeanFT0TOF->SetBinError(bin, MeanFT0TOFError[bin - 1]);
        grMeanFT0TOF->GetXaxis()->SetBinLabel(bin, run.at(bin - 1).Data());
    }
    grMeanFT0TOF->SetMarkerStyle(20);
    grMeanFT0TOF->SetMarkerColor(kBlack);
    grMeanFT0TOF->SetLineColor(kBlack);
    grMeanFT0TOF->SetStats(0);
    grMeanFT0TOF->SetTitle("");
    grMeanFT0TOF->Draw();
    trendFT0TOF->SaveAs(Form("images/TrendFT0TOF.png"));

    TCanvas *trendevTimeTOF = new TCanvas("trendevTimeTOF", "", 1600, 800);
    trendevTimeTOF->SetBottomMargin(0.15);
    trendevTimeTOF->SetLeftMargin(0.15);
    trendevTimeTOF->SetGridx();
    TH1F *grMeanEvTimeTOF = new TH1F("grMeanEvTimeTOF", "trending evTime-TOF", nruns, 0, nruns);
    grMeanEvTimeTOF->SetTitle("trending t0_{TOF}");
    grMeanEvTimeTOF->GetYaxis()->SetTitle("#LT t_{TOF}^{0}#GT (ps)");
    for (int bin = 1; bin <= grMeanEvTimeTOF->GetNbinsX(); bin++)
    {
        grMeanEvTimeTOF->SetBinContent(bin, Meant0TOF[bin - 1]);
        grMeanEvTimeTOF->SetBinError(bin, Meant0TOFError[bin - 1]);
        grMeanEvTimeTOF->GetXaxis()->SetBinLabel(bin, run.at(bin - 1).Data());
    }
    grMeanEvTimeTOF->SetMarkerStyle(20);
    grMeanEvTimeTOF->SetMarkerColor(kBlack);
    grMeanEvTimeTOF->SetLineColor(kBlack);
    grMeanEvTimeTOF->SetStats(0);
    grMeanEvTimeTOF->SetTitle("");
    grMeanEvTimeTOF->Draw();
    trendevTimeTOF->SaveAs(Form("images/Trendt0TOF.png"));

    TCanvas *ctrending = new TCanvas("ctrending", "", 1600, 800);
    ctrending->SetBottomMargin(0.15);
    ctrending->SetLeftMargin(0.15);
    ctrending->SetGridx();
    grMeanEvTimeTOF->SetLineColor(kRed);
    grMeanEvTimeTOF->SetMarkerColor(kRed);
    grMeanFT0TOF->GetYaxis()->SetTitle("");
    grMeanFT0TOF->GetYaxis()->SetRangeUser(-300, 300);
    grMeanFT0TOF->Draw();
    grMeanEvTimeTOF->Draw("SAME");

    TLegend *leg2 = new TLegend(0.7, 0.7, 0.9, 0.9);
    leg2->AddEntry(grMeanFT0TOF, "#LT t0_{FT0}-t0_{TOF} #GT", "LEP");
    leg2->AddEntry(grMeanEvTimeTOF, "#LT t0_{TOF} #GT", "LEP");
    leg2->SetTextSize(0.04);
    leg2->Draw();
    ctrending->SaveAs(Form("images/TrendFT0TOFvst0TOF.png"));
    ctrending->SaveAs(Form("Summary_%s_%s.pdf", period.Data(),pass.Data()));

    ///////////////////////////////////
    //////////// PID //////////////////
    ///////////////////////////////////

    TCanvas *cPID_tof[nruns];
    TCanvas *cPID_tof_summary = new TCanvas("cPID_tof_summary", "", 1000, 1000);
    canvas_multiple(cPID_tof_summary, nruns);
    for (int i = 0; i < nruns; i++)
    {
        cPID_tof[i] = new TCanvas(Form("cPID_tof_%s", run.at(i).Data()), "", 1000, 900);
        canvas_hestetics_single(cPID_tof[i]);
        cPID_tof[i]->SetLogz();
        hBetavsP_ITSTPC_t0TOF[i]->SetStats(0);
        hBetavsP_ITSTPC_t0TOF[i]->SetTitle("t_{0}^{TOF}");
        hBetavsP_ITSTPC_t0TOF[i]->Rebin2D(1, 4);
        hBetavsP_ITSTPC_t0TOF[i]->Draw("colz");

        cPID_tof[i]->SaveAs(Form("images/PID_t0TOF_%s.png", run.at(i).Data()));
        cPID_tof[i]->SaveAs(Form("Summary_Run%s_%s_%s.pdf", run.at(i).Data(), period.Data(), pass.Data()));

        cPID_tof_summary->cd(i + 1);
        cPID_tof_summary->cd(i + 1)->SetLogz();
        hBetavsP_ITSTPC_t0TOF[i]->Draw("colz");
        label->DrawLatex(0.75, 0.95, Form("Run %s", run.at(i).Data()));
    }
    cPID_tof_summary->SaveAs(Form("Summary_%s_%s.pdf", period.Data(),pass.Data()));

    TCanvas *cPID_ft0ac[nruns];
    TCanvas *cPID_ft0ac_summary = new TCanvas("cPID_summary", "", 1000, 1000);
    canvas_multiple(cPID_ft0ac_summary, nruns);
    for (int i = 0; i < nruns; i++)
    {
        cPID_ft0ac[i] = new TCanvas(Form("cPID_ft0ac_%s", run.at(i).Data()), "", 1000, 900);
        canvas_hestetics_single(cPID_ft0ac[i]);
        cPID_ft0ac[i]->SetLogz();
        hBetavsP_ITSTPC_t0FT0AC[i]->SetStats(0);
        hBetavsP_ITSTPC_t0FT0AC[i]->Rebin2D(1, 4);
        hBetavsP_ITSTPC_t0FT0AC[i]->SetTitle("t_{0}^{FT0AC}");
        hBetavsP_ITSTPC_t0FT0AC[i]->Draw("colz");

        cPID_ft0ac[i]->SaveAs(Form("images/PID_t0FT0AC_%s.png", run.at(i).Data()));
        cPID_ft0ac[i]->SaveAs(Form("Summary_Run%s_%s_%s.pdf)", run.at(i).Data(), period.Data(), pass.Data()));

        cPID_ft0ac_summary->cd(i + 1);
        cPID_ft0ac_summary->cd(i + 1)->SetLogz();
        hBetavsP_ITSTPC_t0FT0AC[i]->Draw("colz");
        label->DrawLatex(0.75, 0.95, Form("Run %s", run.at(i).Data()));
    }
    cPID_ft0ac_summary->SaveAs(Form("Summary_%s_%s.pdf)", period.Data(), pass.Data()));

    TFile *write = new TFile(Form("FT0TOF_trending_LHC%s_%s.root", period.Data(), pass.Data()), "RECREATE");
    grMeanFT0TOF->SetName("trend_t0TOFFT0");
    grMeanFT0TOF->Write();
    grMeanEvTimeTOF->SetName("trend_t0TOF");
    grMeanEvTimeTOF->Write();
    ctrending->Write();
    ctrending->Close();
    delete ctrending;
    TDirectory *dir = write->mkdir("Fit");
    dir->cd();
    for (int i = 0; i < nruns; i++)
    {
        cdeltaevtime_tofft0[i]->Write();
        cevtimetof[i]->Write();
        cdeltaevtime_tofft0[i]->Close();
        cevtimetof[i]->Close();
        delete cdeltaevtime_tofft0[i];
        delete cevtimetof[i];
    }
    write->Close();

    TFile *write2 = new TFile(Form("MatchEff_trending_LHC%s_%s.root", period.Data(), pass.Data()), "RECREATE");
    for (int i = 0; i<3; i++){
        htrendEff[i]->Write();
        htrendCorr_tot[i]->Write();
        htrendCorr_ch[i]->Write();
        htrendCorr_trm[i]->Write();
        htrendCorr_drm[i]->Write();
        ctrendacccorr[i]->Write();
        ctrendcorr[i]->Write();
    }
    write2->Close();

    for (int n_run = 0; n_run < nruns; n_run++)
    {
        for (int i_obj = 0; i_obj < n; i_obj++)
        {
            f[i_obj][n_run]->Close();
        }
    }


}

void histo_hestetics(TH1* h, int col = kBlack, int mark = 20){
    h->SetStats(0);
    h->GetYaxis()->SetTitleSize(0.05);
    h->GetXaxis()->SetTitleSize(0.05);
    h->GetYaxis()->SetLabelSize(0.05);
    h->GetXaxis()->SetLabelSize(0.05);
    h->GetYaxis()->SetTitleOffset(1.1);
    h->SetLineColor(col);
    h->SetMarkerColor(col);
    h->SetMarkerStyle(mark);
}

void canvas_hestetics_layout(TCanvas* c, int n = 3, int n1 = 0) {
    c->SetLeftMargin(0.02);
    c->SetBottomMargin(0.02);
    c->SetRightMargin(0.02);
    c->SetTopMargin(0.02);
    c->SetTicky();
    c->SetTickx();
    c->Divide(n,n1);
    for (int i = 1; i <= n ; i++){
        c->cd(i)->SetBottomMargin(0.1);
        c->cd(i)->SetLeftMargin(0.1);
        c->cd(i)->SetRightMargin(0.13);
    }
}

void canvas_hestetics_single(TCanvas* c) {
    c->SetTicky();
    c->SetTickx();
    c->SetLeftMargin(0.15);
    c->SetBottomMargin(0.15);
    c->SetRightMargin(0.15);
    c->SetTopMargin(0.1);
}

void canvas_multiple(TCanvas* c, int n){
    if (n==1) c->Divide(1,1);
    if (n==2) c->Divide(2,1);
    if (n==3) c->Divide(2,2);
    if (n==4) c->Divide(2,2);
    if (n==5) c->Divide(3,2);
    if (n==6) c->Divide(3,2);
    if (n==7) c->Divide(3,3);
    if (n==8) c->Divide(3,3);
    if (n==9) c->Divide(3,3);
    if (n==10) c->Divide(4,3);
    if (n==11) c->Divide(4,3);
    if (n==12) c->Divide(4,3);
    if (n==13) c->Divide(4,4);
    if (n==14) c->Divide(4,4);
    if (n==15) c->Divide(4,4);
    if (n==16) c->Divide(4,4);
    if (n==17) c->Divide(5,4);
    if (n==18) c->Divide(5,4);
    if (n==19) c->Divide(5,4);
    if (n==20) c->Divide(5,4);
    if (n==21) c->Divide(5,4);
    if (n==22) c->Divide(5,4);
    if (n==23) c->Divide(5,4);
    if (n==24) c->Divide(5,4);
    if (n==25) c->Divide(5,5);
    if (n==26) c->Divide(5,5);
    if (n==27) c->Divide(5,5);
    if (n==28) c->Divide(5,5);
    if (n==29) c->Divide(5,5);
    if (n==30) c->Divide(5,5);
}