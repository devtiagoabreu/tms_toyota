#! C:\Perl\bin\perl.exe -I..\common

use strict;
use CGI;
use CGI::Carp qw(fatalsToBrowser);

use TMSstr;
use TMScommon;
use TMSlock;

#require '../common/http_header.pm';

my $lang = &TMSstr::get_lang_set();
&TMSstr::load_str_file($lang);       # 必ず get_str() の前に実行する事！！

my $menu_color = '#0080EF';
my $body_color = '#D5E8F8';

my $html = new CGI;

my $sel_data = $html->param('data');
my $sel_mode = $html->param('sel_mode');
my @shift    = $html->param('shift');
if( $#shift < 0 ){
  require '../common/http_header.pm';
  print &TMScommon::no_data_page( $menu_color, $body_color );
  exit;
}

my @loom_list  = ();
my @style_list = ();
if( $sel_mode eq 'loom' ){
  @loom_list = $html->param('loom');
  if( $#loom_list < 0  ){
    require '../common/http_header.pm';
    print &TMScommon::no_data_page( $menu_color, $body_color );
    exit;
  }
} else{
  @style_list = $html->param('style');
  if( $#style_list < 0 ){
    require '../common/http_header.pm';
    print &TMScommon::no_data_page( $menu_color, $body_color );
    exit;
  }
}

# Excelの制限で、機台数を２５５台に制限
my $colmax = (255 - 1);
if( $#loom_list >= $colmax ){ $#loom_list = $colmax; }

my $update_lock = '../../tmsdata/update.lock';
my $other_user;
if( &TMSlock::check_lockfile($update_lock,$ENV{REMOTE_ADDR},\$other_user) ){	# データ更新中は使用不可
  require '../common/http_header.pm';
  print &TMSlock::data_updating_page( $other_user );
  exit;
}

# 各ファイル名の取得
my $xlsfile  = "../xlsfile/$lang/showstyle.xls";

my $datafile = &TMScommon::get_xlsdata_file_name("showstyle","csv");

my $infofile = "showstyle.tmshlp";


# ---------------------------------------------------------------------
# ＣＳＶファイルの出力
my $now_date = &TMScommon::get_now_date();

open(OUT, "> $datafile" );
print OUT "( $now_date )\n";

@shift = sort @shift;
my $dcount = 0;

# ---------------------------------------------------------------------
# シフト別データの場合

if( $sel_data eq 'shift' ){

  print OUT	&TMScommon::shiftnum_to_shiftname($shift[0])." -> ".
		&TMScommon::shiftnum_to_shiftname($shift[$#shift])."\n".
		"\n\n";

  my @loom  = ();
  foreach my $shiftnum ( @shift ){
    if( open(IN,"< ..\\..\\tmsdata\\shift\\$shiftnum.txt") ){

      my @style = ();
      while(<IN>){
        my $line = $_;

        if( $sel_mode eq 'loom' ){
          if( $line =~ m/,mac_name ([^,]+)/ ){
            my $lm = $1;
            for( my $i=0; $i<=$#loom_list; $i++ ){
              if( $loom_list[$i] eq $lm ){
                if( $line =~ m/,style ([^,]+)/ ){
                  if( length($style[$i]) > 0 ){ $style[$i] .= " "; }
                  $style[$i] .= $1;
                }
                last;
              }
            }
          }
        }
        elsif( $sel_mode eq 'style' ){
          if( $line =~ m/,style ([^,]*)/ ){
            my $st = $1;
            for( my $i=0; $i<=$#style_list; $i++ ){
              if( $style_list[$i] eq $st ){
                if( $line =~ m/,mac_name ([^,]+)/ ){
                  my $n = &TMScommon::entry_to_list(\@loom, $1);
                  if( $n <= $colmax ){		# Excelの制限で、列数を制限
                    if( length($style[$n]) > 0 ){ $style[$n] .= " "; }
                    $style[$n] .= $st;
                  }
                }
                last;
              }
            }
          }
        }

      }
      close(IN);

      if( $#style >= 0 ){
        ++$dcount;
        print OUT &TMScommon::shiftnum_to_shiftname($shiftnum);
        foreach(@style){ print OUT ",=\"$_\""; }
        print OUT "\n";
      }
    }
  }

  # 最終行 -------------------------

  if( $sel_mode eq 'loom' ){ @loom = @loom_list; }

  if( $#loom >= $colmax ){ $#loom = $colmax; }		# Excelの制限で、列数を制限

  print OUT "SHIFT";
  foreach(@loom){ print OUT ",=\"$_\""; }
  print OUT "\n";

}

# ----------------------------------------------------------------------------
# 作業者別データの場合

if( $sel_data eq 'operator' ){

  print OUT	&TMScommon::daynum_to_dayname($shift[0])." -> ".
		&TMScommon::daynum_to_dayname($shift[$#shift])."\n".
		"\n\n";

  my @key_list = ();
  foreach my $shiftnum ( @shift ){
    if( open(IN,"< ..\\..\\tmsdata\\operator\\$shiftnum.txt") ){

      my @style = ();
      while(<IN>){
        my $line = $_;

        if( $sel_mode eq 'loom' ){
          if( $line =~ m/,mac_name ([^,]+)/ ){
            my $lm = $1;
            for( my $i=0; $i<=$#loom_list; $i++ ){
              if( $loom_list[$i] eq $lm ){
                if( $line =~ m/,ope_name ([^,]+)/ ){
                  my $ope = $1;
                  my $n = &TMScommon::entry_to_list(\@key_list,"$lm+&+$ope");
                  if( $n <= $colmax ){	# Excelの制限で、列数を制限
                    if( $line =~ m/,style ([^,]+)/ ){
                      if( length($style[$n]) > 0 ){ $style[$n] .= " "; }
                        $style[$n] .= $1;
                      }
                    }
                  }
                last;
              }
            }
          }
        }
        elsif( $sel_mode eq 'style' ){
          if( $line =~ m/,style ([^,]+)/ ){
            my $st = $1;
            for( my $i=0; $i<=$#style_list; $i++ ){
              if( $style_list[$i] eq $st ){
                if( $line =~ m/,mac_name ([^,]+)/ ){
                  my $lm = $1;
                  if( $line =~ m/,ope_name ([^,]+)/ ){
                    my $ope = $1;
                    my $n = &TMScommon::entry_to_list(\@key_list,"$lm+&+$ope");
                    if( $n <= $colmax ){	# Excelの制限で、列数を制限
                      if( length($style[$n]) > 0 ){ $style[$n] .= " "; }
                        $style[$n] .= $st;
                      }
                    }
                  last;
                }
              }
            }
          }
        }

      }
      close(IN);

      if( $#style >= 0 ){
        ++$dcount;
        print OUT &TMScommon::daynum_to_dayname($shiftnum);
        foreach(@style){ print OUT ",=\"$_\""; }
        print OUT "\n";
      }
    }
  }

  # 最終行 -------------------------

  if( $#key_list > $colmax ){ $#key_list = $colmax; }	# Excelの制限で、列数を制限

  print OUT "DATE";
  foreach(@key_list){ print OUT ",=\"$_\""; }
  print OUT "\n";
}
# ----------------------------------------------------------------------------

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

