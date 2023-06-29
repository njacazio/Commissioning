#include <TStyle.h>

void histo_hestetics(TH1* h, int col, int marker);
void canvas_hestetics_single(TCanvas* c);
void canvas_hestetics_layout(TCanvas* c, int n = 3, int n1 = 0);

void trendingt0(TString period = "22o", TString pass = "apass2")
{

    gStyle->SetOptFit();
    // Get runlist
    system(Form("awk \'{print $1}\' jiratext%s.txt > listofruns%s", period.Data(), period.Data()));
    std::vector<TString> run;
    FILE *file = fopen(Form("listofruns%s", period.Data()), "r");
    char *line;
    size_t len=0;
    while(getline(&line, &len, file) != -1) {
        run.push_back(line);
        run.back().Remove(run.back().Length() - 1);
    }
    fclose(file);

    //MO to check
    TString name[] = {
        "DeltaEvTimeTOFVsFT0CSameBC",
        "EvTimeTOF"};

    const int n = sizeof(name)/sizeof(TString);
    const int nruns = run.size();

    // Open files and get MOs
    TFile* f[n][nruns];
    TH2F* h[n][nruns];
    for (int n_run = 0; n_run < nruns; n_run++)
    {
        for (int i_obj = 0; i_obj < n; i_obj++)
        {
            f[i_obj][n_run] = TFile::Open(Form("Run%s/rootfiles/%s.root", run.at(n_run).Data(), name[i_obj].Data()));
            h[i_obj][n_run] = (TH2F *)f[i_obj][n_run]->Get("ccdb_object");
            h[i_obj][n_run]->SetStats(0);
        }
    }

    TLatex *label = new TLatex();
    label->SetTextFont(42);
    label->SetNDC();
    label->SetTextSize(0.05);
    label->SetTextAlign(22);
    label->SetTextAngle(0);

    TCanvas *cdeltaevtime_tofft0[nruns];
    TF1 *gaus[nruns];
    Double_t MeanFT0TOF[nruns], MeanFT0TOFError[nruns];
    for (int i = 0; i < nruns; i++){
        cdeltaevtime_tofft0[i] = new TCanvas(Form("cdeltaevtime_tofft0_%s", run.at(i).Data()), "", 1000, 800);
        gaus[i] = new TF1("gaus", "gaus", h[0][i]->GetMean() - 300, h[0][i]->GetMean() + 300);

        cdeltaevtime_tofft0[i] ->SetBottomMargin(0.15);
        cdeltaevtime_tofft0[i]->SetBottomMargin(0.15);

        h[0][i]->Draw("HIST");
        h[0][i]->GetXaxis()->SetRangeUser(-1500, 1500);
        h[0][i]->SetLineColor(kBlack);
        h[0][i]->Fit(gaus[i], "0Rq");

        gaus[i]->Draw("SAME");

        MeanFT0TOF[i] = gaus[i]->GetParameter(1);
        MeanFT0TOFError[i] = gaus[i]->GetParError(1);

        label->DrawLatex(0.7,0.85,Form("Mean %.1f", gaus[i]->GetParameter(1)));
        label->DrawLatex(0.7,0.8,Form("Sigma %.1f", gaus[i]->GetParameter(2)));
        label->DrawLatex(0.7,0.75, Form("Chi2/ndf %.1f", gaus[i]->GetChisquare()/gaus[i]->GetNDF()));
        label->DrawLatex(0.3,0.85,Form("Run %s",run.at(i).Data()));

        cdeltaevtime_tofft0[i]->SaveAs(Form("images/Deltaevtimeft0_%s.png", run.at(i).Data()));
    }


    TCanvas *cevtimetof[nruns];
    Double_t Meant0TOF[nruns];
    Double_t Meant0TOFError[nruns];
    TF1 *gaus2[nruns];
    for (int i = 0; i < nruns; i++){
        cevtimetof[i] = new TCanvas(Form("cevtimetof_%s", run.at(i).Data()), "", 1000, 800);
        gaus2[i] = new TF1("gaus", "gaus", h[1][i]->GetMean() - 300, h[1][i]->GetMean() + 300);

        cevtimetof[i]->SetBottomMargin(0.15);
        cevtimetof[i]->SetLeftMargin(0.15);

        for (int bin = 1; bin <= h[1][i]->GetNbinsX(); bin++){
            if (h[1][i]->GetBinContent(bin) > 0.5*h[1][i]->GetMaximum()){
                h[1][i]->SetBinContent(bin,(h[1][i]->GetBinContent(bin-1) + h[1][i]->GetBinContent(bin+1))/2);
            }
        }
        h[1][i]->Fit(gaus2[i], "0Rq");
        h[1][i]->Draw("hist");
        h[1][i]->GetXaxis()->SetRangeUser(-1000, 1000);

        gaus2[i]->Draw("SAME");

        Meant0TOF[i] = gaus2[i]->GetParameter(1);
        Meant0TOFError[i] = gaus2[i]->GetParError(1);

        label->DrawLatex(0.3, 0.85, Form("Run %s", run.at(i).Data()));
        label->DrawLatex(0.7, 0.85, Form("Mean %.1f", gaus2[i]->GetParameter(1)));
        label->DrawLatex(0.7, 0.8, Form("Sigma %.1f", gaus2[i]->GetParameter(2)));
        label->DrawLatex(0.7, 0.75, Form("Chi2/ndf %.1f", gaus2[i]->GetChisquare() / gaus2[i]->GetNDF()));
        label->DrawLatex(0.3, 0.85, Form("Run %s", run.at(i).Data()));

        cevtimetof[i]->SaveAs(Form("images/Evtimetof_%s.png", run.at(i).Data()));
    }

    TCanvas* trendFT0TOF = new TCanvas("trendFT0TOF", "", 1600, 800);
    trendFT0TOF->SetBottomMargin(0.15);
    trendFT0TOF->SetLeftMargin(0.15);
    trendFT0TOF->SetGridx();
    TH1F *grMeanFT0TOF = new TH1F("grMeanFT0TOF", "trending t0_{FT0}-t0_{TOF}", nruns, 0, nruns);
    grMeanFT0TOF->SetTitle("trending FT0-TOF");
    grMeanFT0TOF->GetYaxis()->SetTitle("#LT t_{FT0} - t_{TOF} #GT (ps)");
    for (int bin = 1; bin <= grMeanFT0TOF->GetNbinsX(); bin++){
        grMeanFT0TOF->SetBinContent(bin, MeanFT0TOF[bin-1]);
        grMeanFT0TOF->SetBinError(bin, MeanFT0TOFError[bin-1]);
        grMeanFT0TOF->GetXaxis()->SetBinLabel(bin, run.at(bin-1).Data());
    }
    grMeanFT0TOF->SetMarkerStyle(20);
    grMeanFT0TOF->SetMarkerColor(kBlack);
    grMeanFT0TOF->SetLineColor(kBlack);
    grMeanFT0TOF->SetStats(0);
    grMeanFT0TOF->SetTitle("");
    grMeanFT0TOF->Draw();
    trendFT0TOF->SaveAs(Form("images/TrendFT0TOF.png"));


    TCanvas* trendevTimeTOF = new TCanvas("trendevTimeTOF", "", 1600, 800);
    trendevTimeTOF->SetBottomMargin(0.15);
    trendevTimeTOF->SetLeftMargin(0.15);
    trendevTimeTOF->SetGridx();
    TH1F *grMeanEvTimeTOF = new TH1F("grMeanEvTimeTOF", "trending evTime-TOF", nruns, 0, nruns);
    grMeanEvTimeTOF->SetTitle("trending t0_{TOF}");
    grMeanEvTimeTOF->GetYaxis()->SetTitle("#LT t_{TOF}^{0}#GT (ps)");
    for (int bin = 1; bin <= grMeanEvTimeTOF->GetNbinsX(); bin++){
        grMeanEvTimeTOF->SetBinContent(bin, Meant0TOF[bin-1]);
        grMeanEvTimeTOF->SetBinError(bin, Meant0TOFError[bin-1]);
        grMeanEvTimeTOF->GetXaxis()->SetBinLabel(bin, run.at(bin-1).Data());
    }
    grMeanEvTimeTOF->SetMarkerStyle(20);
    grMeanEvTimeTOF->SetMarkerColor(kBlack);
    grMeanEvTimeTOF->SetLineColor(kBlack);
    grMeanEvTimeTOF->SetStats(0);
    grMeanEvTimeTOF->SetTitle("");
    grMeanEvTimeTOF->Draw();
    trendevTimeTOF->SaveAs(Form("images/Trendt0TOF.png"));

    TCanvas* ctrending = new TCanvas("ctrending", "", 1600, 800);
    ctrending->SetBottomMargin(0.15);
    ctrending->SetLeftMargin(0.15);
    ctrending->SetGridx();
    grMeanEvTimeTOF->SetLineColor(kRed);
    grMeanEvTimeTOF->SetMarkerColor(kRed);
    grMeanFT0TOF->Draw();
    grMeanEvTimeTOF->Draw("SAME");

    TLegend *leg = new TLegend(0.7, 0.7, 0.9, 0.9);
    leg->AddEntry(grMeanFT0TOF, "#LT t0_{FT0}-t0_{TOF} #GT", "LEP");
    leg->AddEntry(grMeanEvTimeTOF, "#LT t0_{TOF} #GT", "LEP");
    leg->SetTextSize(0.04);
    leg->Draw();
    ctrending->SaveAs(Form("images/TrendFT0TOFvst0TOF.png"));

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
    for (int i = 0; i < nruns; i++){
        cdeltaevtime_tofft0[i]->Write();
        cevtimetof[i]->Write();
        cdeltaevtime_tofft0[i]->Close();
        cevtimetof[i]->Close();
        delete cdeltaevtime_tofft0[i];
        delete cevtimetof[i];
    }
    write->Close();
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
}