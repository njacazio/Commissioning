enum ELine {
  kModule = 1,
  kTRM = 2
};

void
plateLines(Int_t flag = kTRM)
{
  
  TLine l;

  /* module lines */
  if (flag & kModule) {
    
    l.SetLineWidth(3);
    l.DrawLine(0, 0, 18, 0);
    l.DrawLine(0, 19, 18, 19);
    l.DrawLine(0, 19+19, 18, 19+19);
    l.DrawLine(0, 19+19+15, 18, 19+19+15);
    l.DrawLine(0, 19+19+15+19, 18, 19+19+15+19);
    l.DrawLine(0, 19+19+15+19+19, 18, 19+19+15+19+19);
    for (Int_t i = 0; i < 19; i++)
      l.DrawLine(i, 0, i, 91);
  }
    
  /* TRM lines */
  if (flag & kTRM) {
    
    l.SetLineWidth(1);
    l.DrawLine(0, 0, 18, 0);
    l.DrawLine(0, 91, 18, 91);
    for (Int_t isec = 0; isec < 18; isec++) {
      l.DrawLine(isec, 0, isec, 91);
      l.DrawLine(isec + 0.5, 0, isec + 0.5, 91);
      for (Int_t itrm = 0; itrm < 10; itrm++) {
	l.DrawLine(isec, 1 + itrm * 5, isec + 0.5, 1 + itrm * 5);
	l.DrawLine(isec + 0.5, itrm * 5, isec + 1, itrm * 5);
      }
      for (Int_t itrm = 0; itrm < 10; itrm++) {
	l.DrawLine(isec + 0.5, 91 - (1 + itrm * 5), isec + 1, 91 - (1 + itrm * 5));
	l.DrawLine(isec, 91 - itrm * 5, isec + 0.5, 91 - itrm * 5);
      }
    }
    l.DrawLine(18, 0, 18, 91);
  }
  
}
