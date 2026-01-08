###################################################################################################
# production.pm
###################################################################################################

use strict;

###################################################################################################

sub make_production_title
{
  my ( $mode, $period, $unit_t ) = @_;

  #### Data Parameter ####

  my $data_type   = 0;
  my $period_type = 0;

  ########################

  my $line = "";
  if(    $period eq "shift" ){ $period_type = 0; $line .= "SHIFT"; }
  elsif( $period eq "date"  ){ $period_type = 1; $line .= "DATE";  }
  elsif( $period eq "week"  ){ $period_type = 2; $line .= "WEEK";  }
  elsif( $period eq "month" ){ $period_type = 3; $line .= "MONTH"; }

  if( $mode eq "shift" ){
    $data_type = 0;
  }
  else{ # "operator"
    $data_type = 1;
    $line .=	",OPERATOR";
  }

  $line .=	",LOOM,STYLE,PRODUCT&$unit_t";

  my $param_key = "PARAM->,data_type,period_type";
  my $param_val = "VALUE->,$data_type,$period_type";

  return $param_key."\n".
	 $param_val."\n".
	 "\n".
	 $line."\n";
}

###################################################################################################

sub make_production_data
{
  my ( $mode, $index, $r_line, $unit ) = @_;
 
  $$r_line =~ s/\n$//;		# 改行コードを削除。
# $$r_line =~ s/\s+/ /g;	# ２個以上のスペースを１個にする。
  my @list = split(/,/,$$r_line);

  my %tmp = ();
  foreach(@list){
    my @data = split(/ /,$_,2);
    if( $#data >= 1 ){ $tmp{$data[0]} = $data[1]; }
  }

  my $mac_name   = $tmp{"mac_name"};
  my $ope_name   = "";
  if( $mode eq "operator" ){ $ope_name = $tmp{"ope_name"}; }
  my $style_name = $tmp{"style"};
  my @seisan     = split(/ /,$tmp{"seisan"});
  my @off_prod   = (0,0,0);  # スキャナオフ時の生産量 2006.1.12 追加
  if( exists $tmp{"off_prod"} ){ @off_prod = split(/ /,$tmp{"off_prod"}); }
  my $run_tm     = $tmp{"run_tm"};
  my $stop_ttm   = $tmp{"stop_ttm"};

  #### Create CSV Data ####

  my $htdata =	"$index";

  if( $mode eq "operator" ){ $htdata .= ",=\"$ope_name\""; }

  $htdata .=	",=\"$mac_name\"".
		",=\"$style_name\"".
		",".($seisan[$unit]+$off_prod[$unit]).
		"\n";

  return $htdata;
}

###################################################################################################
1;
