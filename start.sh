#!/bin/bash
echo "Cleaning Metrics directory"
rm -rf ./Metrics/*
echo "Cleaning stretch directory"
rm -rf ./stretch/*

echo "Starting Ryu Controller"
sudo ryu-manager --observe-links \
    ospf.py
