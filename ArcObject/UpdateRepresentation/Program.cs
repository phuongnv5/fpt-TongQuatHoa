using ESRI.ArcGIS.esriSystem;

using System;
using System.Collections.Generic;
using System.Text;
using System.IO;

using ESRI.ArcGIS.Display;
using ESRI.ArcGIS.Geodatabase;
using ESRI.ArcGIS.DataSourcesGDB;

using Newtonsoft.Json;

namespace ArcgisArcobjects
{
    class Program
    {
        private static LicenseInitializer m_AOLicenseInitializer = new ArcgisArcobjects.LicenseInitializer();

        [STAThread()]
        static void Main(string[] args)
        {
            //ESRI License Initializer generated code.
            m_AOLicenseInitializer.InitializeApplication(new esriLicenseProductCode[] { esriLicenseProductCode.esriLicenseProductCodeAdvanced },
            new esriLicenseExtensionCode[] { });
            //ESRI License Initializer generated code.

            #region "Run"
            //string pathProcessGDB = @"C:\Generalize_25_50\50K_Process.gdb";
            //string pathFileConfig = @"D:\ArcObject_Tools\DemoTools\ArcgisArcobjects\ConfigTool.json";
            if (args[0] == "UpdateRuleID")
            {
                Console.WriteLine(@args[2]);
                RunUpdateRuleID(@args[1], @args[2]);
            }
            else if (args[0] == "UpdateShapeOverride")
            {
                RunUpdateShapeOverride(@args[1], @args[2]);
            }
            #endregion

            #region "WriteFileRuleRepresentation"
            //string pathGDB;
            //string pathFile;

            //pathGDB = @"D:\Official_Data\02_Dulieu\25K\CSDL+bando\5651_4_TB\5651_4_TB.gdb";
            //pathFile = @"D:\ArcObject_Tools\DemoTools\ArcgisArcobjects\Representation25K.txt";
            //WriteFileRuleRepresentation(pathGDB, pathFile);

            //pathGDB = @"D:\Official_Data\02_Dulieu\50K\CSDL\dulieumoi\5651-4\5651_4.gdb";
            //pathFile = @"D:\ArcObject_Tools\DemoTools\ArcgisArcobjects\Representation50K.txt";
            //WriteFileRuleRepresentation(pathGDB, pathFile);
            #endregion

            #region "WriteFileDomain"
            //string pathGDB = @"D:\Official_Data\02_Dulieu\50K\CSDL\dulieumoi\5651-4\5651_4.gdb";
            //string pathFile = @"D:\ArcObject_Tools\DemoTools\ArcgisArcobjects\Domain.txt";
            //string featureDataset = "ThuyHe";
            //string featureClass = "BienA";
            //WriteFileDomain(pathGDB, pathFile);
            #endregion

            #region "WriteFileFeatureClassRepresentation"
            //string pathGDB = @"C:\Generalize_25_50\50K_Process.gdb";
            //string pathFile = @"D:\ArcObject_Tools\DemoTools\ArcgisArcobjects\FeatureClassRepresentation.txt";
            //WriteFileFeatureClassRepresentation(pathGDB, pathFile);
            #endregion

            #region "CreateFileConfig"
            //string pathGDB = @"C:\Generalize_25_50\50K_Process.gdb";
            //string pathFile = @"D:\ArcObject_Tools\DemoTools\ArcgisArcobjects\ConfigTool.json";
            //CreateFileConfig(pathGDB, pathFile);
            #endregion

            #region "Read Domains"
            //string pathGDB = @"D:\Official_Data\02_Dulieu\50K\CSDL\dulieumoi\5651-4\5651_4.gdb";
            //string pathFile = @"D:\ArcObject_Tools\DemoTools\ArcgisArcobjects\Domains.json";
            //ReadDomain(pathGDB, pathFile);
            #endregion

            #region "ReadFeatureClass"
            //string pathGDB = @"C:\Generalize_25_50\50K_Process.gdb";
            //ReadFeatureClass(pathGDB);
            #endregion

            //Do not make any call to ArcObjects after ShutDownApplication()
            m_AOLicenseInitializer.ShutdownApplication();

            Console.WriteLine("Succees...");
            Console.ReadKey();
        }

        static IFeatureClass OpenFeatureClass(IWorkspace iWorkspace, string featureDatasetName, string featureClassName)
        {
            IEnumDataset iEnumDataset = iWorkspace.Datasets[esriDatasetType.esriDTFeatureDataset];
            //iEnumDataset.Reset();

            IDataset iDataset = null;
            while ((iDataset = iEnumDataset.Next()) != null)
            {
                if (iDataset.Name == featureDatasetName)
                {
                    break;
                }
            }
            if (iDataset != null)
            {
                IEnumDataset iEnumDatasetSub = iDataset.Subsets;
                //iEnumDatasetSub.Reset();

                IDataset iDatasetSub = null;
                while ((iDatasetSub = iEnumDatasetSub.Next()) != null)
                {
                    if (iDatasetSub.Name == featureClassName)
                    {
                        break;
                    }
                }
                if (iDatasetSub != null)
                {
                    IFeatureClass iFeatureClass = iDatasetSub as IFeatureClass;
                    return iFeatureClass;
                }
            }
            return null;
        }

        static void UpdateRuleID(IFeatureClass featureClass, IRepresentationWorkspaceExtension iRepresentationWorkspaceExtension, string representationName, int ruleID, string querySQL)
        {
            IRepresentationClass iRepresentationClass = iRepresentationWorkspaceExtension.OpenRepresentationClass(representationName);
            if (iRepresentationClass != null)
            {
                IGeoDataset iGeoDataset = featureClass as IGeoDataset;
                IMapContext iMapContext = new MapContext();
                iMapContext.Init(iGeoDataset.SpatialReference, 50000, iGeoDataset.Extent);

                IQueryFilter iQueryFilter = new QueryFilter();
                iQueryFilter.WhereClause = querySQL;

                IFeatureCursor iFeatureCursor = featureClass.Search(iQueryFilter, true);

                IFeature iFeature = null;
                while ((iFeature = iFeatureCursor.NextFeature()) != null)
                {
                    IRepresentation iRepresentation = iRepresentationClass.GetRepresentation(iFeature, iMapContext);
                    if (iRepresentation != null && iRepresentation.RuleID != ruleID)
                    {
                        Console.WriteLine("\t\tOID: {0}, {1} => {2}", iFeature.OID, iRepresentation.RuleID, ruleID);
                        iRepresentation.RuleID = ruleID;
                        iRepresentation.UpdateFeature();
                        iFeature.Store();
                    }
                }
            }
        }

        static void UpdateShapeOverride(IFeatureClass featureClass, IRepresentationWorkspaceExtension iRepresentationWorkspaceExtension, string representationName)
        {
            IRepresentationClass iRepresentationClass = iRepresentationWorkspaceExtension.OpenRepresentationClass(representationName);

            if (!iRepresentationClass.RequireShapeOverride)
            {
                iRepresentationClass.RequireShapeOverride = true;
            }

            if (iRepresentationClass != null)
            {
                IGeoDataset iGeoDataset = featureClass as IGeoDataset;
                IMapContext iMapContext = new MapContext();
                iMapContext.Init(iGeoDataset.SpatialReference, 50000, iGeoDataset.Extent);

                IFeatureCursor iFeatureCursor = featureClass.Search(null, true);

                IFeature iFeature = null;
                while ((iFeature = iFeatureCursor.NextFeature()) != null)
                {
                    Console.WriteLine("\tOID: {0}, Update Shape Override", iFeature.OID);
                    IRepresentation iRepresentation = iRepresentationClass.GetRepresentation(iFeature, iMapContext);
                    if (iRepresentation.HasShapeOverride)
                    {
                        iRepresentation.Shape.SetEmpty();
                    }
                    iRepresentation.Shape = iFeature.Shape;
                    iRepresentation.UpdateFeature();
                    iFeature.Store();
                }
            }
        }

        static void RunUpdateRuleID(string pathProcessGDB, string pathFileConfig)
        {
            IWorkspaceFactory iWorkspaceFactory = new FileGDBWorkspaceFactoryClass();
            IWorkspace iWorkspace = iWorkspaceFactory.OpenFromFile(pathProcessGDB, 0);

            IRepresentationWorkspaceExtension iRepresentationWorkspaceExtension = GetRepresentationFromFeatureClass(iWorkspace);

            List<ConfigTool> listConfig = ReadFileConfig(pathFileConfig);

            foreach (ConfigTool elemConfig in listConfig)
            {
                foreach (FeatureClass elemFeatureClass in elemConfig.listFeatureClass)
                {
                    IFeatureClass featureClass = OpenFeatureClass(iWorkspace, elemConfig.nameFeatureDataset, elemFeatureClass.nameFeatureClass);
                    if (featureClass != null)
                    {
                        foreach (Representation elemRepresentation in elemFeatureClass.listRepresentation)
                        {
                            Console.WriteLine("Process: {0}/{1}, Representation: {2}",
                                elemConfig.nameFeatureDataset, elemFeatureClass.nameFeatureClass, elemRepresentation.nameRepresentation);
                            foreach (Rule elemRule in elemRepresentation.listRule)
                            {
                                int ruleID;
                                if ((int.TryParse(elemRule.ruleID, out ruleID)) && (elemRule.querySQL != ""))
                                {
                                    Console.WriteLine("\tRuleID: {0}, QuerySQL: {1}", ruleID, elemRule.querySQL);
                                    UpdateRuleID(featureClass, iRepresentationWorkspaceExtension, elemRepresentation.nameRepresentation, ruleID, elemRule.querySQL);
                                }
                            }
                        }
                    }
                }
            }
        }

        static void RunUpdateShapeOverride(string pathProcessGDB, string pathFileConfig)
        {
            IWorkspaceFactory iWorkspaceFactory = new FileGDBWorkspaceFactoryClass();
            IWorkspace iWorkspace = iWorkspaceFactory.OpenFromFile(pathProcessGDB, 0);

            IRepresentationWorkspaceExtension iRepresentationWorkspaceExtension = GetRepresentationFromFeatureClass(iWorkspace);

            List<ConfigTool> listConfig = ReadFileConfig(pathFileConfig);

            foreach (ConfigTool elemConfig in listConfig)
            {
                foreach (FeatureClass elemFeatureClass in elemConfig.listFeatureClass)
                {
                    IFeatureClass featureClass = OpenFeatureClass(iWorkspace, elemConfig.nameFeatureDataset, elemFeatureClass.nameFeatureClass);
                    if (featureClass != null)
                    {
                        foreach (Representation elemRepresentation in elemFeatureClass.listRepresentation)
                        {
                            Console.WriteLine("Process: {0}/{1}, Representation: {2}",
                                elemConfig.nameFeatureDataset, elemFeatureClass.nameFeatureClass, elemRepresentation.nameRepresentation);
                            UpdateShapeOverride(featureClass, iRepresentationWorkspaceExtension, elemRepresentation.nameRepresentation);
                        }
                    }
                }
            }
        }

        public static IRepresentationWorkspaceExtension GetRepresentationFromFeatureClass(IWorkspace iWorkspace)
        {
            IWorkspaceExtensionManager iWorkspaceExtensionManager = (IWorkspaceExtensionManager)iWorkspace;
            UIDClass uIDClass = new UIDClass();
            uIDClass.Value = "{FD05270A-8E0B-4823-9DEE-F149347C32B6}";
            return (IRepresentationWorkspaceExtension)iWorkspaceExtensionManager.FindExtension(uIDClass);
        }

        static void WriteFileRuleRepresentation(string pathGDB, string pathFile)
        {
            System.IO.FileStream fileStream = File.Open(pathFile, FileMode.Create);

            IWorkspaceFactory iWorkspaceFactory = new FileGDBWorkspaceFactoryClass();
            IWorkspace iWorkspace = iWorkspaceFactory.OpenFromFile(pathGDB, 0);

            IEnumDataset iEnumDataset = iWorkspace.Datasets[esriDatasetType.esriDTRepresentationClass];
            iEnumDataset.Reset();

            IDataset iDataset = null;
            List<string> representationName = new List<string>();
            while ((iDataset = iEnumDataset.Next()) != null)
            {
                representationName.Add(iDataset.Name);
            }
            representationName.Sort();
            for (int index = 0; index < representationName.Count; index++)
            {
                string textFile;
                textFile = string.Format("################# {0} #################\n", representationName[index]);
                IRepresentationWorkspaceExtension iRepresentationWorkspaceExtension = GetRepresentationFromFeatureClass(iWorkspace);
                IRepresentationClass iRepresentationClass = iRepresentationWorkspaceExtension.OpenRepresentationClass(representationName[index]);
                IRepresentationRules iRepresentationRules = iRepresentationClass.RepresentationRules;
                int iD;
                IRepresentationRule iRepresentationRule = null;
                iRepresentationRules.Next(out iD, out iRepresentationRule);
                while (iRepresentationRule != null)
                {
                    textFile += string.Format("\t{0} : {1}\n", iD, iRepresentationRules.Name[iD]);
                    iRepresentationRules.Next(out iD, out iRepresentationRule);
                }
                Encoding textUTF8 = Encoding.UTF8;
                fileStream.Write(textUTF8.GetBytes(textFile), 0, textUTF8.GetByteCount(textFile));
            }
            fileStream.Close();
        }

        static void WriteFileDomain(string pathGDB, string featureDataset, string featureClass, string pathFile)
        {
            System.IO.FileStream fileStream = File.Open(pathFile, FileMode.Create);

            IWorkspaceFactory iWorkspaceFactory = new FileGDBWorkspaceFactoryClass();
            IWorkspace iWorkspace = iWorkspaceFactory.OpenFromFile(pathGDB, 0);

            IEnumDataset iEnumDataset = iWorkspace.Datasets[esriDatasetType.esriDTFeatureDataset];
            iEnumDataset.Reset();

            IDataset iDataset = null;
            while ((iDataset = iEnumDataset.Next()) != null)
            {
                if (iDataset.Name == featureDataset)
                {
                    break;
                }
            }
            if (iDataset != null)
            {
                IEnumDataset iEnumDatasetSub = iDataset.Subsets;
                //iEnumDatasetSub.Reset();

                IDataset iDatasetSub = null;
                while ((iDatasetSub = iEnumDatasetSub.Next()) != null)
                {
                    if (iDatasetSub.Name == featureClass)
                    {
                        break;
                    }
                }
                if (iDatasetSub != null)
                {
                    string textFile = "";

                    IFeatureClass iFeatureClass = iDatasetSub as IFeatureClass;

                    IFields iFields = iFeatureClass.Fields;
                    for (int index = 0; index < iFields.FieldCount; index++)
                    {
                        IField iField = iFields.Field[index];

                        IDomain iDomain = iField.Domain;
                        if (iDomain != null)
                        {
                            ICodedValueDomain iCodedValueDomain = iDomain as ICodedValueDomain;
                            textFile += string.Format("Name: {0}, CodeCount: {1}, Field: {2}\n", iDomain.Name, iCodedValueDomain.CodeCount, iFields.Field[index].Name);
                            for (int indexSub = 0; indexSub < iCodedValueDomain.CodeCount; indexSub++)
                            {
                                textFile += string.Format("\tValue: {0}, Name: {1}\n", iCodedValueDomain.Value[indexSub], iCodedValueDomain.Name[indexSub]);
                            }
                        }
                    }
                    Encoding textUTF8 = Encoding.UTF8;
                    fileStream.Write(textUTF8.GetBytes(textFile), 0, textUTF8.GetByteCount(textFile));
                }
                fileStream.Close();
            }
        }

        static void WriteFileFeatureClassRepresentation(string pathGDB, string pathFile)
        {
            System.IO.FileStream fileStream = File.Open(pathFile, FileMode.Create);

            IWorkspaceFactory iWorkspaceFactory = new FileGDBWorkspaceFactoryClass();
            IWorkspace iWorkspace = iWorkspaceFactory.OpenFromFile(pathGDB, 0);

            IRepresentationWorkspaceExtension iRepresentationWorkspaceExtension = GetRepresentationFromFeatureClass(iWorkspace);

            IEnumDataset iEnumDataset = iWorkspace.Datasets[esriDatasetType.esriDTFeatureDataset];
            //iEnumDataset.Reset();

            IDataset iDataset = null;
            while ((iDataset = iEnumDataset.Next()) != null)
            {
                string textFile = string.Format("FeatureDataset: {0}", iDataset.Name);
                IEnumDataset iEnumDatasetSub = iDataset.Subsets;
                IDataset iDatasetSub = null;
                while ((iDatasetSub = iEnumDatasetSub.Next()) != null)
                {
                    textFile += string.Format("\n\tFeatureClass: {0}, UseRepresentation: {1}",
                        iDatasetSub.Name, iRepresentationWorkspaceExtension.FeatureClassHasRepresentations[iDatasetSub as IFeatureClass]);
                    if (iRepresentationWorkspaceExtension.FeatureClassHasRepresentations[iDatasetSub as IFeatureClass])
                    {
                        IEnumDatasetName iEnumDatasetName = iRepresentationWorkspaceExtension.FeatureClassRepresentationNames[iDatasetSub as IFeatureClass];
                        IDatasetName iDatasetName = null;
                        while ((iDatasetName = iEnumDatasetName.Next()) != null)
                        {
                            textFile += string.Format("\n\t\tFeatureClassRepresentation: {0}", iDatasetName.Name);
                        }
                    }
                }
                textFile += "\n";
                Encoding textUTF8 = Encoding.UTF8;
                fileStream.Write(textUTF8.GetBytes(textFile), 0, textUTF8.GetByteCount(textFile));
            }
            fileStream.Close();
        }

        static void WriteFileDomain(string pathGDB, string pathFile)
        {
            System.IO.FileStream fileStream = File.Open(pathFile, FileMode.Create);

            IWorkspaceFactory iWorkspaceFactory = new FileGDBWorkspaceFactoryClass();
            IWorkspace iWorkspace = iWorkspaceFactory.OpenFromFile(pathGDB, 0);

            IEnumDataset iEnumDataset = iWorkspace.Datasets[esriDatasetType.esriDTFeatureDataset];
            iEnumDataset.Reset();

            IDataset iDataset = null;
            while ((iDataset = iEnumDataset.Next()) != null)
            {

                IEnumDataset iEnumDatasetSub = iDataset.Subsets;
                //iEnumDatasetSub.Reset();

                IDataset iDatasetSub = null;
                while ((iDatasetSub = iEnumDatasetSub.Next()) != null)
                {
                    string textFile = string.Format("################### {0}/{1} ###################\n", iDataset.Name, iDatasetSub.Name);
                    IFeatureClass iFeatureClass = iDatasetSub as IFeatureClass;

                    IFields iFields = iFeatureClass.Fields;
                    for (int index = 0; index < iFields.FieldCount; index++)
                    {
                        IField iField = iFields.Field[index];

                        IDomain iDomain = iField.Domain;
                        if (iDomain != null)
                        {
                            ICodedValueDomain iCodedValueDomain = iDomain as ICodedValueDomain;
                            textFile += string.Format("Name: {0}, CodeCount: {1}, Field: {2}\n", iDomain.Name, iCodedValueDomain.CodeCount, iFields.Field[index].Name);
                            for (int indexSub = 0; indexSub < iCodedValueDomain.CodeCount; indexSub++)
                            {
                                textFile += string.Format("\tValue: {0}, Name: {1}\n", iCodedValueDomain.Value[indexSub], iCodedValueDomain.Name[indexSub]);
                            }
                        }
                    }
                    Encoding textUTF8 = Encoding.UTF8;
                    fileStream.Write(textUTF8.GetBytes(textFile), 0, textUTF8.GetByteCount(textFile));
                }
            }
            fileStream.Close();
        }

        static void CreateFileConfig(string pathGDB, string pathFile)
        {
            IWorkspaceFactory iWorkspaceFactory = new FileGDBWorkspaceFactoryClass();
            IWorkspace iWorkspace = iWorkspaceFactory.OpenFromFile(pathGDB, 0);

            IRepresentationWorkspaceExtension iRepresentationWorkspaceExtension = GetRepresentationFromFeatureClass(iWorkspace);

            IEnumDataset iEnumDataset = iWorkspace.Datasets[esriDatasetType.esriDTFeatureDataset];

            List<ConfigTool> listConfig = new List<ConfigTool>();

            IDataset iDataset = null;
            while ((iDataset = iEnumDataset.Next()) != null)
            {
                ConfigTool objectConfig = new ConfigTool();
                objectConfig.nameFeatureDataset = iDataset.Name;

                IEnumDataset iEnumDatasetSub = iDataset.Subsets;
                IDataset iDatasetSub = null;
                while ((iDatasetSub = iEnumDatasetSub.Next()) != null)
                {
                    if (iRepresentationWorkspaceExtension.FeatureClassHasRepresentations[iDatasetSub as IFeatureClass])
                    {
                        FeatureClass featureClass = new FeatureClass();
                        featureClass.nameFeatureClass = iDatasetSub.Name;
                        objectConfig.listFeatureClass.Add(featureClass);

                        IEnumDatasetName iEnumDatasetName = iRepresentationWorkspaceExtension.FeatureClassRepresentationNames[iDatasetSub as IFeatureClass];
                        IDatasetName iDatasetName = null;
                        while ((iDatasetName = iEnumDatasetName.Next()) != null)
                        {
                            Representation representation = new Representation();
                            representation.nameRepresentation = iDatasetName.Name;
                            featureClass.listRepresentation.Add(representation);

                            IRepresentationClass iRepresentationClass = iRepresentationWorkspaceExtension.OpenRepresentationClass(iDatasetName.Name);
                            IRepresentationRules iRepresentationRules = iRepresentationClass.RepresentationRules;
                            int iD;
                            IRepresentationRule iRepresentationRule = null;
                            iRepresentationRules.Next(out iD, out iRepresentationRule);

                            Rule rule = new Rule();
                            rule.ruleID = "0";
                            rule.nameRule = "null";
                            representation.listRule.Add(rule);

                            while (iRepresentationRule != null)
                            {
                                rule = new Rule();
                                rule.ruleID = iD.ToString();
                                rule.nameRule = iRepresentationRules.Name[iD];
                                representation.listRule.Add(rule);
                                iRepresentationRules.Next(out iD, out iRepresentationRule);
                            }
                        }
                    }
                }
                if (objectConfig.listFeatureClass.Count > 0)
                {
                    listConfig.Add(objectConfig);
                }
            }

            string strListConfig = JsonConvert.SerializeObject(listConfig, Formatting.Indented);

            Encoding textUTF8 = Encoding.UTF8;
            File.WriteAllText(pathFile, strListConfig, Encoding.UTF8);
        }

        static List<ConfigTool> ReadFileConfig(string pathFile)
        {
            return JsonConvert.DeserializeObject<List<ConfigTool>>(File.ReadAllText(pathFile));
        }

        static void ReadDomain(string pathGDB, string pathFile)
        {
            IWorkspaceFactory iWorkspaceFactory = new FileGDBWorkspaceFactoryClass();
            IWorkspace iWorkspace = iWorkspaceFactory.OpenFromFile(pathGDB, 0);

            IWorkspaceDomains iWorkspaceDomains = iWorkspace as IWorkspaceDomains;

            IEnumDomain iEnumDomain = iWorkspaceDomains.Domains;

            List<Domain> listDomain = new List<Domain>();

            IDomain iDomain = null;

            while ((iDomain = iEnumDomain.Next()) != null)
            {
                if (iDomain.Type == esriDomainType.esriDTCodedValue)
                {
                    Domain domain = new Domain();
                    domain.domainName = iDomain.Name;
                    domain.domainID = iDomain.DomainID.ToString();
                    domain.domainAliasName = iDomain.Owner;
                    ICodedValueDomain iCodedValueDomain = iDomain as ICodedValueDomain;
                    if (iCodedValueDomain != null)
                    {
                        for (int index = 0; index < iCodedValueDomain.CodeCount; index++)
                        {
                            NameValue nameValue = new NameValue();
                            nameValue.name = iCodedValueDomain.Name[index];
                            nameValue.value = iCodedValueDomain.Value[index].ToString();
                            domain.listNameValue.Add(nameValue);
                        }
                    }
                    if (domain.listNameValue.Count > 0)
                    {
                        listDomain.Add(domain);
                    }
                }
            }

            string strListDomain = JsonConvert.SerializeObject(listDomain, Formatting.Indented);

            Encoding textUTF8 = Encoding.UTF8;
            File.WriteAllText(pathFile, strListDomain, Encoding.UTF8);
        }

        static void ReadFeatureClass(string pathProcessGDB)
        {
            IWorkspaceFactory iWorkspaceFactory = new FileGDBWorkspaceFactoryClass();
            IWorkspace iWorkspace = iWorkspaceFactory.OpenFromFile(pathProcessGDB, 0);
            IFeatureClass featureClass = OpenFeatureClass(iWorkspace, "DanCuCoSoHaTang", "KhuChucNangP");
            IFeatureCursor iFeatureCursor = featureClass.Search(null, true);
            IFeature iFeature = null;
            while((iFeature = iFeatureCursor.NextFeature()) != null)
            {
                Console.WriteLine("doiTuong: {0}, loaiKhuChucNang: {1}", iFeature.Value[6], iFeature.Value[9]);
            }
        }
    }
}
