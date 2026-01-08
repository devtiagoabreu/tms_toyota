#! C:\Perl\bin\perl.exe -I..\common

use strict;
use CGI;
use CGI::Carp qw(fatalsToBrowser);

use TMSstr;
use TMScommon;
use TMSlock;
use TMSselitem;

#require '../common/http_header.pm';

my $lang = &TMSstr::get_lang_set();
&TMSstr::load_str_file($lang);       # 必ず get_str() の前に実行する事！！

my $menu_color = '#426AB3';
my $body_color = '#E1E2F2';

my $html = new CGI;

my $sel_mode = $html->param('sel_mode');

my %loom  = ();
my %style = ();
if( $sel_mode eq 'loom' ){
  my @p = $html->param('loom');
  if( $#p < 0 ){
    require '../common/http_header.pm';
    print &TMScommon::no_data_page( $menu_color, $body_color );
    exit;
  }
  foreach(@p){ $loom{$_} = 1; }
} else{
  my @p = $html->param('style');
  if( $#p < 0 ){
    require '../common/http_header.pm';
    print &TMScommon::no_data_page( $menu_color, $body_color );
    exit;
  }
  foreach(@p){ $style{$_} = 1; }
}

my $period = $html->param('period');
my @shift  = $html->param('shift');
@shift = sort @shift;

my @file = ();
my @index = ();
&TMScommon::get_shift_file_list( $period, \@shift, \@file, \@index );	# @file:  期間(@shift)にマッチするファイル名
									# @index: 期間(@shift)の表示用文字列

my $update_lock = '../../tmsdata/update.lock';
my $other_user;
if( &TMSlock::check_lockfile($update_lock,$ENV{REMOTE_ADDR},\$other_user) ){	# データ更新中は使用不可
  require '../common/http_header.pm';
  print &TMSlock::data_updating_page( $other_user );
  exit;
}

# 各ファイル名の取得
my $xlsfile = "../xlsfile/$lang/stylereport.xls";

my $datafile = &TMScommon::get_xlsdata_file_name("stylereport","csv");

my $infofile = "stylereport.tmshlp";


# ＣＳＶファイルの出力
my @val_item2     = &TMSselitem::get_value_of_item2();
my @val_item      = &TMSselitem::get_value_of_item();
my @val_item3     = &TMSselitem::get_value_of_item3();
my @val_detail    = &TMSselitem::get_value_of_detail();
my @val_color     = &TMSselitem::get_value_of_color();
my $val_beam_type = &TMSselitem::get_value_of_beam_type();
my $val_unit      = &TMSselitem::get_value_of_unit();

my @ttl_item2  = &TMSselitem::get_title_of_item2();
my @ttl_item   = &TMSselitem::get_title_of_item();
my @ttl_item3  = &TMSselitem::get_title_of_item3();
my @ttl_detail = &TMSselitem::get_title_of_detail();
my @ttl_color  = &TMSselitem::get_title_of_color();
my $ttl_unit   = &TMSselitem::get_title_of_unit();

my $jat_ari = &TMSselitem::is_jat_ari(),
my $lwt_ari = &TMSselitem::is_lwt_ari(),


open(OUT, "> $datafile" );

my $now_date = &TMScommon::get_now_date();

print OUT	"( $now_date )\n".
		"$index[0] -> $index[$#index]\n".
		"\n";

print OUT &make_stylereport_title( $period,
				   $jat_ari, $lwt_ari,
				   $val_beam_type,
				   $ttl_unit,
				   \@val_item2,  \@ttl_item2,
				   \@val_item,   \@ttl_item,
				   \@val_item3,  \@ttl_item3,
				   \@val_detail, \@ttl_detail,
				   \@val_color,  \@ttl_color  );

my $dcount = 0;
for( my $i=0; $i<=$#file; $i++ ){
  my $f = $file[$i];
  open(IN,"< $f");
  while(<IN>){
    my $line = $_;
    my $m = 0;
    if( $sel_mode eq "loom" ){
      if( $line =~ m/,mac_name ([^,]+)/ ){
        if( exists($loom{$1}) ){ $m = 1; }
      }
    } else{  # "style"
      if( $line =~ m/,style ([^,]+)/ ){
        if( exists($style{$1}) ){ $m = 1; }
      }
    }
    if( $m ){

      $dcount++;
      print OUT &make_stylereport_data(	$index[$i],
					\$line,
					$val_beam_type,
					$val_unit,
					\@val_item2,
					\@val_item,
					\@val_item3,
					\@val_detail,
					\@val_color  );

    }
  }
  close(IN);
}
close(OUT);


if( $dcount == 0 ){
  require '../common/http_header.pm';
  print &TMScommon::no_data_page( $menu_color, $body_color );
}
else{
  # TmsHelper.exe 用情報データ出力
  &TMScommon::http_header_tmsinf($infofile);

  print "method POPUP_EXCEL\n";
  print "version 1.0\n";

  print "xlsfile ". &TMScommon::get_fullpath_url($xlsfile). "\n";

  if( $ENV{REMOTE_ADDR} eq '127.0.0.1' ){  # ローカルの場合（データ読み込み高速化の為）
    print "csvfile1 ". &TMScommon::get_fullpath_file($datafile). "\n";
  }else{  # リモートの場合
    print "csvfile1 ". &TMScommon::get_fullpath_url($datafile). "\n";
  }

  #print "macro start_make_all\n";
}

exit;

###################################################################################################
###################################################################################################

sub make_stylereport_title
{
  my ( $period, $jat_ari, $lwt_ari, $beam_type, $unit_t,
       $r_item2_v,$r_item2_t, $r_item_v,$r_item_t, $r_item3_v,$r_item3_t,
       $r_detail_v,$r_detail_t, $r_color_v,$r_color_t ) = @_;

  #### Data Parameter ####

  my $period_type = 0;
  my $sort_col   = 0;
  my $run        = 0;
  my $stop       = 0;
  my $rpm        = 0;
  my $effic      = 0;
  my $production = 0;
  my $mac_stop   = 0;
  my $yarn_stop  = 0;
  my $unselect   = 0;
  my $unselect2  = 0;
  my $main_col   = 0;
  my $detail     = 0;

  ########################

  my $line =	"";
  if(    $period eq "shift" ){ $period_type = 0; $line .= "SHIFT"; }
  elsif( $period eq "date"  ){ $period_type = 1; $line .= "DATE";  }
  elsif( $period eq "week"  ){ $period_type = 2; $line .= "WEEK";  }
  elsif( $period eq "month" ){ $period_type = 3; $line .= "MONTH"; }

  $line .= ",LOOM,SORTKEY,STYLE,LOOM_COUNT";
  $sort_col += 2;
  $main_col += 2;

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
      $line .=	",$dt&COUNT,$dt&MINUTE";
      $mac_stop += 1;
      $main_col += 2;
    }
    else{ $unselect = 1; }
  }
  for( my $i=0; $i<=1; $i++ ){  # (0)WarpTop, (1)Warp
    if( $$r_item_v[$i] ){
      my $dt = $$r_item_t[$i];
      $line .=	",$dt&COUNT,$dt&MINUTE,$dt&RATE_PH,$dt&RATE_PDAY,$dt&RATE_PP";
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
    $line .=	",$dt&COUNT,$dt&MINUTE,$dt&RATE_PH,$dt&RATE_PDAY,$dt&RATE_PP";
    $yarn_stop += 1;
    $main_col += 5;
  }
  else{ $unselect = 1; $unselect2 = 1; }

  #for( my $i=2; $i<=4; $i++ ){  # (2)False, (3)Leno(R), (4)Leno(L)
  #  if( $$r_item_v[$i] ){
  #    my $dt = $$r_item_t[$i];
  #    $line .=	",$dt&COUNT,$dt&MINUTE,$dt&RATE_PH,$dt&RATE_PP";
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

  my $param_key = "PARAM->,period_type,jat_ari,lwt_ari,sort_col,rpm,effic,run,stop,production";
  my $param_val = "VALUE->,$period_type,$jat_ari,$lwt_ari,$sort_col,$rpm,$effic,$run,$stop,$production";

  $param_key .= ",mac_stop,yarn_stop,unselect,unselect2,main_col,detail";
  $param_val .= ",$mac_stop,$yarn_stop,$unselect,$unselect2,$main_col,$detail";

  return $param_key."\n".
	 $param_val."\n".
	 "\n".
	 $line."\n";

}


###################################################################################################

sub make_stylereport_data
{
  my ( $index, $r_line, $beam_type, $unit,
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

  my $htdata =	"$index".              # シフト名
		",=\"$mac_name\",".    # 機台名、SORTKEY
		",=\"$style_name\",";  # 品種名、機台数

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
  if( $$r_item3[0] ){ $htdata .= ",$stop_ct[3],$stop_tm[3],,,"; }

  # CC Back
  if( $$r_item3[1] ){ $htdata .= ",$stop_ct[11],$stop_tm[11],,,"; }

  # Leno(L), Leno(R)
  for( my $i=3; $i<=4; $i++ ){
    if( $$r_item[$i] ){ $htdata .= ",$stop_ct[$i],$stop_tm[$i],,,"; }
  }

  return $htdata."\n";
}

