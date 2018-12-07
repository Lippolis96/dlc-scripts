#include "dlcgui.h"
#include "ui_dlcgui.h"

dlcgui::dlcgui(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::dlcgui)
{
    ui->setupUi(this);
}

dlcgui::~dlcgui()
{
    delete ui;
}
