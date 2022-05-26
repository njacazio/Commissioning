void canvas_hestetics_single(TCanvas* c);
void canvas_hestetics_layout(TCanvas* c, int n = 3, int n1 = 0);

void drawqcplots(TString run = ""){

    TString name[] = {
        "hOrbitID", 
        "hSlotPartMask", 
        "hHits", 
        "hEffRDHTriggers", 
        "RDHCounter", 
        "DRMCounter", 
        "TRMCounterSlot03", 
        "TRMCounterSlot04", 
        "TRMCounterSlot05", 
        "TRMCounterSlot06", 
        "TRMCounterSlot07", 
        "TRMCounterSlot08", 
        "TRMCounterSlot09", 
        "hIndexEOIsNoise", 
        "hIndexEOHitRate", 
        "HitMap" ,
        "ToT_Integrated" ,
        "ToT_SectorIA" ,
        "ToT_SectorIC" ,
        "ToT_SectorOA" ,
        "ToT_SectorOC" ,
        "Multiplicity_Integrated" ,
        "Multiplicity_SectorIA" ,
        "Multiplicity_SectorIC" ,
        "Multiplicity_SectorOA",
        "Multiplicity_SectorOC",
        "Time_Integrated" ,
        "Time_SectorIA" ,
        "Time_SectorIC" ,
        "Time_SectorOC" ,
        "Time_SectorOC" ,
        "Time_Orphans" ,
        "ReadoutWindowSize" ,
        "OrbitVsCrate" , 
        "mean_of_hits",
        "mean_of_hits"
        };    
    
    const int n = sizeof(name)/sizeof(TString);
    TFile* f[n];    
    TH2F* h[n];
    for (int i = 0; i < n; i++){
        f[i] = TFile::Open(Form("Run%s/rootfiles/%s.root",run.Data(),name[i].Data()));
        h[i] = (TH2F*)f[i]->Get("ccdb_object");
        h[i]->SetStats(0);
    }
    TCanvas* c1 = (TCanvas*)f[n-1]->Get("ccdb_object");

    TLatex *label = new TLatex();
	label->SetTextFont(42);
    label-> SetNDC();
    label-> SetTextSize(0.06);
    label-> SetTextAlign(22);
    label-> SetTextAngle(0);

    TCanvas* c = new TCanvas("c","",2800,1200);
    canvas_hestetics_layout(c,0,1);
    
    h[0]->Draw("colz");
    c->Print(Form("QCRun%s.pdf(",run.Data()),"pdf");

    for (int i = 1; i < n-1; i++){
        if (i==13) {h[i]->Draw("HIST");
        } else { h[i]->Draw("colz");}
        c->Print(Form("QCRun%s.pdf",run.Data()),"pdf");
    }
    c1->Print(Form("QCRun%s.pdf)",run.Data()),"pdf");
}

void canvas_hestetics_layout(TCanvas* c, int n = 3, int n1 = 0) {
    c->SetLeftMargin(0.1);
    c->SetBottomMargin(0.2);
    c->SetRightMargin(0.15);
    c->SetTopMargin(0.1);
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