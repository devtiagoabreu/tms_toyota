###################################################################################################
# shiftreport.pm
###################################################################################################

use strict;

###################################################################################################

sub make_shiftreport_title
{
  my ( $mode, $period, $sel, $jat_ari, $lwt_ari, $beam_type, $unit_t,
       $r_item2_v,$r_item2_t, $r_item_v,$r_item_t, $r_item3_v,$r_item3_t,
       $r_detail_v,$r_detail_t, $r_color_v,$r_color_t ) = @_;

  #### Data Parameter ####

  my $data_type   = 0;
  my $period_type = 0;
  my $sort_col    = 0;
  my $run         = 0;
  my $stop        = 0;
  my $rpm         = 0;
  my $effic       = 0;
  my $production  = 0;
  my $mac_stop    = 0;
  my $yarn_stop   = 0;
  my $unselect    = 0;
  my $unselect2   = 0;
  my $main_col    = 0;
  my $detail      = 0;

  ########################

  my $line = "SORTKEY,";

  if(    $period eq "shift" ){ $period_type = 0; $line .= "SHIFT"; }
  elsif( $period eq "date"  ){ $period_type = 1; $line .= "DATE";  }
  elsif( $period eq "week"  ){ $period_type = 2; $line .= "WEEK";  }
  elsif( $period eq "month" ){ $period_type = 3; $line .= "MONTH"; }
  $sort_col += 1;
  $main_col += 1;

  if( $mode eq "shift" ){
    $data_type = 0;
  }
  else{ # "operator"
    $data_type = 1;
    $line .= ",OPERATOR"; $sort_col += 1; $main_col += 1;
  }

  if( ($jat_ari == 1) and ($lwt_ari == 1) ){
    if( $sel eq "loom" ){ $line .= ",LOOM,MAC_TYPE,STYLE"; }
    else{                 $line .= ",STYLE,LOOM,MAC_TYPE"; }
    $sort_col += 3;
    $main_col += 3;
  }else{
    if( $sel eq "loom" ){ $line .= ",LOOM,STYLE"; }
    else{                 $line .= ",STYLE,LOOM"; }
    $sort_col += 2;
    $main_col += 2;
  }

  for( my $i=0; $i<=3; $i++ ){
    if( $$r_item2_v[$i] ){  # (0)Top Beam, (1)Beam, (2)RPM, (3) Effic
      $line .= ",$$r_item2_t[$i]";
      if(    $i <= 1 ){ $sort_col += 1; }
      elsif( $i == 2 ){ $rpm   = 1; }
      elsif( $i == 3 ){ $effic = 1; }
      $main_col += 1;
    }
  }

  if( $$r_item2_v[4] ){ $run  = 1; }  # (4)Run
  if( $$r_item2_v[5] ){ $stop = 1; }  # (5)Stop
  $line .= ",$$r_item2_t[4],$$r_item2_t[5],$$r_item2_t[6]&PICK";  # (4)Run, (5)Stop, Production(pick)
  $main_col += 3;

  if( $$r_item2_v[6] ){ $line .= ",$$r_item2_t[6]&$unit_t"; $production = 1; $main_col += 1; }  # (6)Production

  for( my $i=6; $i<=$#$r_item_v; $i++ ){  # (6)WarpOut, (7)ClothDoff, (8)ManualStop, (9)PowerOff, (10)Other
    if( $$r_item_v[$i] ){
      my $dt = $$r_item_t[$i];
      $line .= ",$dt&COUNT,$dt&MINUTE";
      $mac_stop += 1;
      $main_col += 2;
    }
    else{ $unselect = 1; }
  }
  for( my $i=0; $i<=1; $i++ ){  # (0)WarpTop, (1)Warp
    if( $$r_item_v[$i] ){
      my $dt = $$r_item_t[$i];
      $line .= ",$dt&COUNT,$dt&MINUTE,$dt&RATE_PH,$dt&RATE_PDAY,$dt&RATE_PP";
      $yarn_stop += 1;
      $main_col += 5;
    }
    else{
      if( ($i == 0) && ($beam_type != 2) ){ next; }  # Top Beam 無し
      $unselect = 1; $unselect2 = 1;
    }
  }

  if( $$r_item_v[5] ){  # (5)Weft, 
    my $dt = $$r_item_t[5];
    $line .= ",$dt&COUNT,$dt&MINUTE,$dt&RATE_PH,$dt&RATE_PDAY,$dt&RATE_PP";
    $yarn_stop += 1;
    $main_col += 5;
  }
  else{ $unselect = 1; $unselect2 = 1; }

  #for( my $i=2; $i<=4; $i++ ){  # (2)False, (3)Leno(R), (4)Leno(L)
  #  if( $$r_item_v[$i] ){
  #    my $dt = $$r_item_t[$i];
  #    $line .= ",$dt&COUNT,$dt&MINUTE,$dt&RATE_PH,$dt&RATE_PP";
  #    $yarn_stop += 1;
  #    $main_col += 4;
  #  }
  #  else{ $unselect = 1; $unselect2 = 1; }
  #}

  # (2)False / CC Total
  if( $$r_item_v[2] ){
    my $dt = $$r_item_t[2];
    $line .= ",$dt&COUNT,$dt&MINUTE,$dt&RATE_PH,$dt&RATE_PDAY,$dt&RATE_PP";
    $yarn_stop += 1;
    $main_col += 5;
  }
  else{ $unselect = 1; $unselect2 = 1; }

  # Leno Total
  if( $$r_item3_v[2] ){
    my $dt = $$r_item3_t[2];
    $line .= ",$dt&COUNT,$dt&MINUTE,$dt&RATE_PH,$dt&RATE_PDAY,$dt&RATE_PP";
    $yarn_stop += 1;
    $main_col += 5;
  }
  else{ $unselect = 1; $unselect2 = 1; }

  # Unselect（回数／時間用）
  if( $unselect  ){ $line .= ",UNSELECT&COUNT,UNSELECT&MINUTE"; $main_col += 2; }

  # Unselect（ミス率用）
  if( $unselect2 ){ $line .= ",UNSELECT2&COUNT,UNSELECT&RATE_PH,UNSELECT&RATE_PDAY,UNSELECT&RATE_PP"; $main_col += 4; }

  # Total
  $line .= ",TOTAL&COUNT,TOTAL&MINUTE,TOTAL2&COUNT,TOTAL&RATE_PH,TOTAL&RATE_PDAY,TOTAL&RATE_PP";
  $main_col += 6;

  # ----------------------------------------------------------------------------------

  # WF1, WF2, LH
  for( my $i=0; $i<=$#$r_detail_v; $i++ ){
    if( $$r_detail_v[$i] ){
      my $dt = $$r_detail_t[$i];
      for( my $j=0; $j<=$#$r_color_v; $j++ ){
        if( $$r_color_v[$j] ){
          my $col = $$r_color_t[$j];
          $line .= ",$dt&$col&COUNT,$dt&$col&MINUTE,$dt&$col&RATE_PH,$dt&$col&RATE_PDAY,$dt&$col&RATE_PP";
          $detail += 1;
        }
      }
    }
  }

  # CC Front, CC Back
  for( my $i=0; $i<=1; $i++ ){
    if( $$r_item3_v[$i] ){
      my $dt = $$r_item3_t[$i];
      $line .= ",$dt&COUNT,$dt&MINUTE,$dt&RATE_PH,$dt&RATE_PDAY,$dt&RATE_PP";
      $detail += 1;
    }
  }

  # Leno(L), Leno(R)
  for( my $i=3; $i<=4; $i++ ){
    if( $$r_item_v[$i] ){
      my $dt = $$r_item_t[$i];
      $line .= ",$dt&COUNT,$dt&MINUTE,$dt&RATE_PH,$dt&RATE_PDAY,$dt&RATE_PP";
      $detail += 1;
    }
  }

  # ----------------------------------------------------------------------------------

  my $param_key = "PARAM->,data_type,period_type,jat_ari,lwt_ari,sort_col,rpm,effic,run,stop,production";
  my $param_val = "VALUE->,$data_type,$period_type,$jat_ari,$lwt_ari,$sort_col,$rpm,$effic,$run,$stop,$production";

  $param_key .= ",mac_stop,yarn_stop,unselect,unselect2,main_col,detail";
  $param_val .= ",$mac_stop,$yarn_stop,$unselect,$unselect2,$main_col,$detail";

  return $param_key."\n".
	 $param_val."\n".
	 "\n".
	 $line."\n";

}


###################################################################################################

sub make_shiftreport_data
{
  my ( $mode, $index, $sel, $r_line, $jat_lwt_ari, $beam_type, $unit,
       $r_item2, $r_item, $r_item3, $r_detail, $r_color ) = @_;
 
  $$r_line =~ s/\n$//;		# 改行コードを削除。
# $$r_line =~ s/\s+/ /g;	# ２個以上のスペースを１個にする。
  my @list = split(/,/,$$r_line);

  my %tmp = ();
  foreach(@list){
    my @data = split(/ /,$_,2);
    if( $#data >= 1 ){ $tmp{$data[0]} = $data[1]; }
  }

  my $mac_name   = $tmp{"mac_name"};
  my $mac_type   = "JAT";
  if( exists $tmp{"mac_type"} ){ $mac_type = $tmp{"mac_type"}; }
  my $ope_name   = "";
  if( $mode eq "operator" ){ $ope_name = $tmp{"ope_name"}; }
  my $style_name = $tmp{"style"};
  my $beam       = $tmp{"beam"};
  my $ubeam      = $tmp{"ubeam"};
  my @seisan     = split(/ /,$tmp{"seisan"});
  my @off_prod   = (0,0,0);  # スキャナオフ時の生産量 2006.1.12 追加
  if( exists $tmp{"off_prod"} ){ @off_prod = split(/ /,$tmp{"off_prod"}); }
  my $run_tm     = $tmp{"run_tm"};
  my $stop_ttm   = $tmp{"stop_ttm"};
  my @stop_ct    = split(/ /,$tmp{"stop_ct"});
  my @stop_tm    = split(/ /,$tmp{"stop_tm"});
  my @wf1_ct     = split(/ /,$tmp{"wf1_ct"});
  my @wf1_tm     = split(/ /,$tmp{"wf1_tm"});
  my @wf2_ct     = split(/ /,$tmp{"wf2_ct"});
  my @wf2_tm     = split(/ /,$tmp{"wf2_tm"});
  my @lh_ct      = split(/ /,$tmp{"lh_ct"});
  my @lh_tm      = split(/ /,$tmp{"lh_tm"});

  # Ver3.0以前の旧データ対応
  if( $#stop_ct < 11 ){ $stop_ct[11] = 0; }  # CC後
  if( $#stop_tm < 11 ){ $stop_tm[11] = 0; }  #

  #### Create CSV Data ####

  my $htdata = "";	# Sort Key

  $htdata .=	",$index";

  if( $mode eq "operator" ){ $htdata .=	",=\"$ope_name\""; }

  if( $jat_lwt_ari ){
    if( $sel eq "loom" ){
      $htdata .= ",=\"$mac_name\",=\"$mac_type\"".
                 ",=\"$style_name\"";
    } else{  # "style"
      $htdata .= ",=\"$style_name\"".
                 ",=\"$mac_name\",=\"$mac_type\"";
    }
  }else{
    if( $sel eq "loom" ){
      $htdata .= ",=\"$mac_name\"".
                 ",=\"$style_name\"";
    } else{  # "style"
      $htdata .= ",=\"$style_name\"".
                 ",=\"$mac_name\"";
    }
  }

  if( $$r_item2[0] ){ $htdata .= ",=\"$ubeam\""; }
  if( $$r_item2[1] ){ $htdata .= ",=\"$beam\"";  }
  if( $$r_item2[2] ){ $htdata .= ",";            }  # rpm
  if( $$r_item2[3] ){ $htdata .= ",";            }  # effic

  $htdata .=	",$run_tm".
		",$stop_ttm".
		",$seisan[0]";		# pick off_prodは不要

  if( $$r_item2[6] ){ $htdata .= ",".($seisan[$unit]+$off_prod[$unit]); }

  my $unsel = 0;
  my $unsel_ct = 0;
  my $unsel_tm = 0;
  my $total_tm = 0;
  my $total_ct = 0;

  for( my $i=6; $i<=$#$r_item; $i++ ){  # (6)WarpOut, (7)ClothDoff, (8)ManualStop, (9)PowerOff, (10)Other
    if( $$r_item[$i] ){  $htdata .= ",$stop_ct[$i],$stop_tm[$i]"; }
    else{ $unsel = 1; $unsel_ct += $stop_ct[$i]; $unsel_tm += $stop_tm[$i]; }
    $total_ct += $stop_ct[$i]; $total_tm += $stop_tm[$i];
  }

  my $unsel2 = 0;
  my $unsel2_ct = 0;
  my $total2_ct = 0;

  for( my $i=0; $i<=1; $i++ ){  # (0)WarpTop, (1)Warp
    if( $$r_item[$i] ){  $htdata .= ",$stop_ct[$i],$stop_tm[$i],,,"; }
    else{
      if( ($i == 0) && ($beam_type != 2) ){ next; }  # Top Beam 無し
      $unsel  = 1; $unsel_ct  += $stop_ct[$i]; $unsel_tm += $stop_tm[$i];
      $unsel2 = 1; $unsel2_ct += $stop_ct[$i];
    }
    $total_ct  += $stop_ct[$i]; $total_tm += $stop_tm[$i];
    $total2_ct += $stop_ct[$i];
  }

  {
    my $i = 5;   # (5)Weft, 
    if( $$r_item[$i] ){  $htdata .= ",$stop_ct[$i],$stop_tm[$i],,,"; }
    else{ $unsel  = 1; $unsel_ct  += $stop_ct[$i]; $unsel_tm += $stop_tm[$i];
          $unsel2 = 1; $unsel2_ct += $stop_ct[$i]; }
    $total_ct  += $stop_ct[$i]; $total_tm += $stop_tm[$i];
    $total2_ct += $stop_ct[$i];
  }

  #for( my $i=2; $i<=4; $i++ ){  # (2)False, (3)Leno(R), (4)Leno(L)
  #  if( $$r_item[$i] ){  $htdata .= ",$stop_ct[$i],$stop_tm[$i],,"; }
  #  else{ $unsel  = 1; $unsel_ct  += $stop_ct[$i]; $unsel_tm += $stop_tm[$i];
  #        $unsel2 = 1; $unsel2_ct += $stop_ct[$i]; }
  #  $total_ct  += $stop_ct[$i]; $total_tm += $stop_tm[$i];
  #  $total2_ct += $stop_ct[$i];
  #}

  # (2)False / CC Total
  my $false_ct = $stop_ct[2] + $stop_ct[11];  # CC前+CC後
  my $false_tm = $stop_tm[2] + $stop_tm[11];
  if( $$r_item[2] ){ $htdata .= ",$false_ct,$false_tm,,,"; }
  else{ $unsel  = 1; $unsel_ct  += $false_ct; $unsel_tm += $false_tm;
        $unsel2 = 1; $unsel2_ct += $false_ct; }
  $total_ct  += $false_ct; $total_tm += $false_tm;
  $total2_ct += $false_ct;

  # Leno Total
  my $leno_ct = $stop_ct[3] + $stop_ct[4];  # LenoL+LenoR
  my $leno_tm = $stop_tm[3] + $stop_tm[4];
  if( $$r_item3[2] ){ $htdata .= ",$leno_ct,$leno_tm,,,"; }
  else{ $unsel  = 1; $unsel_ct  += $leno_ct; $unsel_tm += $leno_tm;
        $unsel2 = 1; $unsel2_ct += $leno_ct; }
  $total_ct  += $leno_ct; $total_tm += $leno_tm;
  $total2_ct += $leno_ct;

  # UnSelect（回数／時間用）
  if( $unsel  ){ $htdata .= ",$unsel_ct,$unsel_tm"; }

  # UnSelect2（ミス率用）
  if( $unsel2 ){ $htdata .= ",$unsel2_ct,,,"; }

  # Total
  $htdata .= ",$total_ct,$total_tm,$total2_ct,,,";

  # ----------------------------------------------------------------------------------

  if( $$r_detail[0] ){ # WF1
    for( my $i=0; $i<=$#$r_color; $i++ ){
      if( $$r_color[$i] ){ $htdata .= ",$wf1_ct[$i],$wf1_tm[$i],,,"; }
    }
  }
  if( $$r_detail[1] ){ # WF2
    for( my $i=0; $i<=$#$r_color; $i++ ){
      if( $$r_color[$i] ){ $htdata .= ",$wf2_ct[$i],$wf2_tm[$i],,,"; }
    }
  }
  if( $$r_detail[2] ){ # LH
    for( my $i=0; $i<=$#$r_color; $i++ ){
      if( $$r_color[$i] ){ $htdata .= ",$lh_ct[$i],$lh_tm[$i],,,"; }
    }
  }

  # CC Front
  if( $$r_item3[0] ){ $htdata .= ",$stop_ct[2],$stop_tm[2],,,"; }

  # CC Back
  if( $$r_item3[1] ){ $htdata .= ",$stop_ct[11],$stop_tm[11],,,"; }

  # Leno(L), Leno(R)
  for( my $i=3; $i<=4; $i++ ){
    if( $$r_item[$i] ){ $htdata .= ",$stop_ct[$i],$stop_tm[$i],,,"; }
  }

  return $htdata."\n";
}

###################################################################################################
1;
