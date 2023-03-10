

void EtaPhimacro(int iPt = 0)
{
  TFile *out_Plots = new TFile("out_Plots.root");
  TMultiGraph *mg = (TMultiGraph *)out_Plots->Get(Form("EtaPhiPt%d", iPt));
  const TString colors[11] = {"#a6cee3", "#1f78b4", "#b2df8a", "#33a02c", "#fb9a99", "#e31a1c", "#fdbf6f", "#ff7f00", "#cab2d6", "#6a3d9a", "#ffff99"};
  TCanvas *can = new TCanvas();
  auto *frame = can->DrawFrame(0,-2000, 7, 10000, ";Phi;DD");
  for (Int_t i = 0; i < mg->GetListOfGraphs()->GetEntries(); i++)
  {
    auto *g = (TGraphErrors *)mg->GetListOfGraphs()->At(i);
    int col = TColor::GetColor(colors[i]);
    g->SetLineWidth(2);
    g->SetMarkerSize(1.2);
    g->SetLineColor(col);
    g->SetMarkerColor(col);
    g->SetTitle(g->GetName());
    mg->GetListOfGraphs()->At(i)->Draw("LP");
  }
  can->BuildLegend();
}