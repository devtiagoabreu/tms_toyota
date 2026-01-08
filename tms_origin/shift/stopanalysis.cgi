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
@shift = sort @shift;		# 配列をソートする。

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
my $xlsfile   = "../xlsfile/$lang/stopanalysis.xls";

my $countfile = &TMScommon::get_xlsdata_file_name("stopanalysis_c","csv");
my $timefile  = &TMScommon::get_xlsdata_file_name("stopanalysis_t","csv");

my $infofile = "stopanalysis.tmshlp";


# ＣＳＶファイルの出力
my @val_item      = &TMSselitem::get_value_of_item();
my @val_item3     = &TMSselitem::get_value_of_item3();
my @val_detail    = &TMSselitem::get_value_of_detail();
my @val_color     = &TMSselitem::get_value_of_color();
my $val_beam_type = &TMSselitem::get_value_of_beam_type();

my @ttl_item   = &TMSselitem::get_title_of_item();
my @ttl_item3  = &TMSselitem::get_title_of_item3();
my @ttl_detail = &TMSselitem::get_title_of_detail();
my @ttl_color  = &TMSselitem::get_title_of_color();


open(CNT, "> $countfile" );
open(TIM, "> $timefile" );

my $now_date = &TMScommon::get_now_date();

print CNT	"( $now_date )\n".
		"$index[0] -> $index[$#index]\n".
		"\n";

print TIM	"( $now_date )\n".
		"$index[0] -> $index[$#index]\n".
		"\n";

my $htdata =  &make_stopanalysis_title(	$period,
					\@val_item,   \@ttl_item,
					\@val_item3,  \@ttl_item3,
					\@val_detail, \@ttl_detail,
					\@val_color,  \@ttl_color,
					$val_beam_type	);
print CNT $htdata;
print TIM $htdata;


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

      my $count = "";
      my $time  = "";
      &make_stopanalisys_data(	$index[$i],
				\$line,
				\$count,
				\$time,
				\@val_item,
				\@val_item3,
				\@val_detail,
				\@val_color,
				$val_beam_type );
      print CNT $count;
      print TIM $time;

    }
  }
  close(IN);
}
close(CNT);
close(TIM);


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
    print "csvfile1 ". &TMScommon::get_fullpath_file($countfile). "\n";
    print "csvfile2 ". &TMScommon::get_fullpath_file($timefile). "\n";
  }else{  # リモートの場合
    print "csvfile1 ". &TMScommon::get_fullpath_url($countfile). "\n";
    print "csvfile2 ". &TMScommon::get_fullpath_url($timefile). "\n";
  }

  #print "macro start_make_all\n";
}

exit;

###################################################################################################

sub make_stopanalysis_title
{
  my ( $period,
       $r_item_v,   $r_item_t,
       $r_item3_v,  $r_item3_t,
       $r_detail_v, $r_detail_t,
       $r_color_v,  $r_color_t,
       $beam_type ) = @_;

  #### Data Parameter ####

  my $period_type = 0;

  ########################

  my $line =	"";
  if(    $period eq "shift" ){ $period_type = 0; $line .= "SHIFT"; }
  elsif( $period eq "date"  ){ $period_type = 1; $line .= "DATE";  }
  elsif( $period eq "week"  ){ $period_type = 2; $line .= "WEEK";  }
  elsif( $period eq "month" ){ $period_type = 3; $line .= "MONTH"; }

  $line .=	",LOOM,STYLE";
  my $unsel = 0;

  for( my $i=0; $i<=1; $i++ ){  # (0)WarpTop, (1)Warp
    if( $$r_item_v[$i] ){
      $line .=	",$$r_item_t[$i]";
    }
    else{
      if( ($i == 0) && ($beam_type != 2) ){ next; }  # Top Beam 無し
      $unsel = 1;
    }
  }

  if( $$r_item_v[5] ){  # (5)Weft

    if( $$r_detail_v[0] || $$r_detail_v[1] || $$r_detail_v[2] ){
      for( my $i=0; $i<=2; $i++ ){
        if( $$r_detail_v[$i] ){
          my $dt = $$r_detail_t[$i];
          for( my $j=0; $j<=$#$r_color_v; $j++ ){
            if( $$r_color_v[$j] ){
              $line .=	",$dt&$$r_color_t[$j]";
            }
          }
        }
      }
      $line .=	",WEFT_OTHER";
    }

    else{
      $line .=	",$$r_item_t[5]";
    }
  }
  else{ $unsel = 1; }

  #for( my $i=2; $i<=4; $i++ ){  # (2)False, (3)Leno(R), (4)Leno(L)
  #  if( $$r_item_v[$i] ){
  #    $line .=	",$$r_item_t[$i]";
  #  }
  #  else{ $unsel = 1; }
  #}

  if( $$r_item3_v[0] or $$r_item3_v[1] ){ # CC前､CC後のどちらか設定で両方表示
    $line .= ",$$r_item3_t[0],$$r_item3_t[1]";
  }
  elsif( $$r_item_v[2] ){  # (2)False/CC合計
    $line .= ",$$r_item_t[2]";
  }else{
    $unsel = 1;
  }

  if( $$r_item_v[3] or $$r_item_v[4] ){ # (3)Leno(R)､(4)Leno(L)のどちらか設定で両方表示
    $line .= ",$$r_item_t[3],$$r_item_t[4]";
  }
  elsif( $$r_item3_v[2] ){  # Leno合計
    $line .= ",$$r_item3_t[2]";
  }else{
    $unsel = 1;
  }

  for( my $i=6; $i<=$#$r_item_v; $i++ ){  # (6)WarpOut, (7)ClothDoff, (8)ManualStop, (9)PowerOff, (10)Other
    if( $$r_item_v[$i] ){
      $line .=	",$$r_item_t[$i]";
    }
    else{ $unsel = 1; }
  }

  if( $unsel ){  # UnSelect
    $line .=	",UNSELECT";
  }

  my $param_key = "PARAM->,period_type";
  my $param_val = "VALUE->,$period_type";

  return $param_key."\n".
	 $param_val."\n".
	 "\n".
	 $line."\n";
}

###################################################################################################

sub make_stopanalisys_data
{
  my ( $index, $r_line, $r_count, $r_time,
       $r_item, $r_item3, $r_detail, $r_color, $beam_type ) = @_;

  $$r_line =~ s/\n$//;		# 改行コードを削除。
# $$r_line =~ s/\s+/ /g;	# ２個以上のスペースを１個にする。
  my @list = split(/,/,$$r_line);

  my %tmp = ();
  foreach(@list){
    my @data = split(/ /,$_,2);
    if( $#data >= 1 ){ $tmp{$data[0]} = $data[1]; }
  }

  my $mac_name = $tmp{"mac_name"};
  my $style    = $tmp{"style"};
  my $run_tm   = $tmp{"run_tm"};
  my $stop_ttm = $tmp{"stop_ttm"};
  my @stop_ct  = split(/ /,$tmp{"stop_ct"});
  my @stop_tm  = split(/ /,$tmp{"stop_tm"});
  my @wf1_ct   = split(/ /,$tmp{"wf1_ct"});
  my @wf1_tm   = split(/ /,$tmp{"wf1_tm"});
  my @wf2_ct   = split(/ /,$tmp{"wf2_ct"});
  my @wf2_tm   = split(/ /,$tmp{"wf2_tm"});
  my @lh_ct    = split(/ /,$tmp{"lh_ct"});
  my @lh_tm    = split(/ /,$tmp{"lh_tm"});

  # Ver3.0以前の旧データ対応
  if( $#stop_ct < 11 ){ $stop_ct[11] = 0; }  # CC後
  if( $#stop_tm < 11 ){ $stop_tm[11] = 0; }  #

  #### Create CSV Data ####

  $$r_count = "$index,=\"$mac_name\",=\"$style\"";
  $$r_time  = "$index,=\"$mac_name\",=\"$style\"";

  my $unsel = 0;
  my $unsel_ct = 0;
  my $unsel_tm = 0;

  for( my $i=0; $i<=1; $i++ ){  # (0)WarpTop, (1)Warp
    if( $$r_item[$i] ){
      $$r_count .= ",$stop_ct[$i]";
      $$r_time  .= ",$stop_tm[$i]";
    } else{
      if( ($i == 0) && ($beam_type != 2) ){ next; }  # Top Beam 無し
      $unsel = 1;
      $unsel_ct += $stop_ct[$i];
      $unsel_tm += $stop_tm[$i];
    }
  }

  if( $$r_item[5] ){  # (5)Weft
    if( $$r_detail[0] || $$r_detail[1] || $$r_detail[3] ){

      my $wother_ct = 0;
      my $wother_tm = 0;

      # WF1
      for( my $i=0; $i<=$#$r_color; $i++ ){
        if( $$r_detail[0] && $$r_color[$i] ){
          $$r_count .= ",$wf1_ct[$i]";
          $$r_time  .= ",$wf1_tm[$i]";
        } else{
          $wother_ct += $wf1_ct[$i];
          $wother_tm += $wf1_tm[$i];
        }
      }
      # WF2
      for( my $i=0; $i<=$#$r_color; $i++ ){
        if( $$r_detail[1] && $$r_color[$i] ){
          $$r_count .= ",$wf2_ct[$i]";
          $$r_time  .= ",$wf2_tm[$i]";
        } else{
          $wother_ct += $wf2_ct[$i];
          $wother_tm += $wf2_tm[$i];
        }
      }
      # LH
      for( my $i=0; $i<=$#$r_color; $i++ ){
        if( $$r_detail[2] && $$r_color[$i] ){
          $$r_count .= ",$lh_ct[$i]";
          $$r_time  .= ",$lh_tm[$i]";
        } else{
          $wother_ct += $lh_ct[$i];
          $wother_tm += $lh_tm[$i];
        }
      }

      $$r_count .= ",$wother_ct";
      $$r_time  .= ",$wother_tm";
    }
    else{
      $$r_count .= ",$stop_ct[5]";
      $$r_time  .= ",$stop_tm[5]";
    }
  }
  else{
    $unsel = 1;
    $unsel_ct += $stop_ct[5];
    $unsel_tm += $stop_tm[5];
  }

  #for( my $i=2; $i<=4; $i++ ){  # (2)False, (3)Leno(R), (4)Leno(L)
  #  if( $$r_item[$i] ){
  #    $$r_count .= ",$stop_ct[$i]";
  #    $$r_time  .= ",$stop_tm[$i]";
  #  } else{
  #    $unsel = 1;
  #    $unsel_ct += $stop_ct[$i];
  #    $unsel_tm += $stop_tm[$i];
  #  }
  #}

  if( $$r_item3[0] or $$r_item3[1] ){ # CC前､CC後のどちらか設定で両方表示
    $$r_count .= ",$stop_ct[2],$stop_ct[11]";
    $$r_time  .= ",$stop_tm[2],$stop_ct[11]";
  }
  elsif( $$r_item[2] ){  # (2)False/CC合計
    $$r_count .= ",".($stop_ct[2] + $stop_ct[11]);
    $$r_time  .= ",".($stop_tm[2] + $stop_ct[11]);
  }else{
    $unsel = 1;
    $unsel_ct += ($stop_ct[2] + $stop_ct[11]);
    $unsel_tm += ($stop_tm[2] + $stop_ct[11]);
  }

  if( $$r_item[3] or $$r_item[4] ){ # (3)Leno(R)､(4)Leno(L)のどちらか設定で両方表示
    $$r_count .= ",$stop_ct[3],$stop_ct[4]";
    $$r_time  .= ",$stop_tm[3],$stop_ct[4]";
  }
  elsif( $$r_item3[2] ){  # Leno合計
    $$r_count .= ",".($stop_ct[3] + $stop_ct[4]);
    $$r_time  .= ",".($stop_tm[3] + $stop_ct[4]);
  }else{
    $unsel = 1;
    $unsel_ct += ($stop_ct[3] + $stop_ct[4]);
    $unsel_tm += ($stop_tm[3] + $stop_ct[4]);
  }

  for( my $i=6; $i<=$#$r_item; $i++ ){  # (6)WarpOut, (7)ClothDoff, (8)ManualStop, (9)PowerOff, (10)Other
    if( $$r_item[$i] ){
      $$r_count .= ",$stop_ct[$i]";
      $$r_time  .= ",$stop_tm[$i]";
    } else{
      $unsel = 1;
      $unsel_ct += $stop_ct[$i];
      $unsel_tm += $stop_tm[$i];
    }
  }

  if( $unsel ){  # UnSelect
    $$r_count .= ",$unsel_ct";
    $$r_time  .= ",$unsel_tm";
  }

  $$r_count .= "\n";
  $$r_time  .= "\n";

}

###################################################################################################

