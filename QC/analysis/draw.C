void histo_hestetics(TH1* h);
void canvas_hestetics_single(TCanvas* c);
void canvas_hestetics_layout(TCanvas* c, int n = 3, int n1 = 0);

void draw(TString run = "505285"){

    /*
    [0] hHits
    [1] hSlotPartMask
    [2] hIndexEOIsNoise
    [3] hIndexEOInTimeWin
    [4] hIndexEOHitRate
    [5] TOFRawsMulti
    [6] TOFRawHitMap
    [7] TOFRawsTime
    [8] OrbitDDL 
    [9] mean_of_hits
    */

    const int n = 10; 
    TString name[n] = {"hHits", "hSlotPartMask", "hIndexEOIsNoise", "hIndexEOInTimeWin", "hIndexEOHitRate", "TOFRawsMulti", "TOFRawHitMap", "TOFRawsTime", "OrbitDDL", "mean_of_hits"};    
    TFile* f[n];    
    TH1F* h[n];
    for (int i = 0; i < n; i++){
        f[i] = TFile::Open(Form("Run%s/%s.root",run.Data(),name[i].Data()));
        h[i] = (TH1F*)f[i]->Get("ccdb_object");
        //histo_hestetics(h[i]);
    }

    TLatex *label = new TLatex();
	label->SetTextFont(42);
    label-> SetNDC();
    label-> SetTextSize(0.06);
    label-> SetTextAlign(22);
    label-> SetTextAngle(0);

    //---------------------------------
    //-----------NOISE-----------------
    //---------------------------------
    TCanvas* cnoise = new TCanvas("cnoise","",1600,1250);
    canvas_hestetics_layout(cnoise,0,2);
    cnoise->cd(1);
    cnoise->cd(1)->SetLogy();
    h[4]->Draw("HIST");  
    label-> DrawLatex(0.25, 0.8, Form("Run %s", run.Data()));     
    cnoise->cd(2);
    cnoise->cd(2)->SetLogy();
    h[3]->Draw("HIST");
    h[3]->SetTitle("All channels, noisy in red");
    h[2]->SetLineColor(kRed);
    h[2]->Draw("HIST SAME"); 
    cnoise->SaveAs(Form("Run%s/noise_layout.png",run.Data()));

    //---------------------------------
    //-----------RAW-----------------
    //---------------------------------
    TCanvas* craw = new TCanvas("craw","",1800,550);
    canvas_hestetics_layout(craw,2);
    craw->cd(1);
    craw->cd(1)->SetLogy();
    h[0]->SetLineWidth(2);
    h[0]->Draw();  
    label-> DrawLatex(0.25, 0.8, Form("Run %s", run.Data()));     
    craw->cd(2);
    //craw->cd(2)->SetLogz();
    h[1]->Draw("colz"); 
    craw->cd(3);
    craw->SaveAs(Form("Run%s/raw_layout.png",run.Data()));
    
    //---------------------------------
    //-----------DIGITS-----------------
    //---------------------------------
    TCanvas* cdig = new TCanvas("cdig","",1800,850);
    canvas_hestetics_layout(cdig,2,2);
    cdig->cd(1);
    cdig->cd(1)->SetLogz();
    h[6]->Draw("colz"); 
    label-> DrawLatex(0.25, 0.8, Form("Run %s", run.Data()));     
    cdig->cd(2);
    h[5]->Draw();       
    cdig->cd(3);
    h[7]->Draw(); 
    cdig->cd(4);
    h[8]->Draw("colz");  
    cdig->SaveAs(Form("Run%s/digits_layout.png",run.Data()));

    //---------------------------------
    //-----------TRENDING-----------------
    //---------------------------------
    TCanvas* ctrend = new TCanvas("ctrend","",1800,800);
    h[9]->Draw();
    ctrend->SaveAs("trending.png");

    TCanvas* csingle[n];
    for (int i = 0; i < n-1; i++){
        csingle[i] = new TCanvas(Form("c_%s",name[i].Data()),"",1200,800);
        if(i==0 || i==2 || i==3 || i==4)csingle[i]->SetLogy();
        if(i==6)csingle[i]->SetLogz();
        h[i]->Draw("colz HIST");
        label-> DrawLatex(0.27, 0.8, Form("Run %s", run.Data()));     
        csingle[i]->SaveAs(Form("Run%s/%s.png",run.Data(),name[i].Data()));
        csingle[i]->SaveAs(Form("Run%s/%s.root",run.Data(),name[i].Data()));
    }
}

void histo_hestetics(TH1* h){
    //h->SetStats(0);
    //h->GetYaxis()->SetTitleSize(0.05);
    //h->GetXaxis()->SetTitleSize(0.05);
    
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