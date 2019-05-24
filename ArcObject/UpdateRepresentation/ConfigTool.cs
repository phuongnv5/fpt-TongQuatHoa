using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ArcgisArcobjects
{
    class Rule
    {
        public string ruleID;
        public string nameRule;
        public string querySQL;
        public Rule()
        {
            querySQL = "";
        }
    }
    class Representation
    {
        public string nameRepresentation;
        public List<Rule> listRule;
        public Representation()
        {
            listRule = new List<Rule>();
        }
    }
    class FeatureClass
    {
        public string nameFeatureClass;
        public List<Representation> listRepresentation;
        public FeatureClass()
        {
            listRepresentation = new List<Representation>();
        }
    }
    class ConfigTool
    {
        public string nameFeatureDataset;
        public List<FeatureClass> listFeatureClass;
        public ConfigTool()
        {
            listFeatureClass = new List<FeatureClass>();
        }
    }

    //Class Domain
    class Domain
    {
        public string domainAliasName;
        public string domainName;
        public string domainID;
        public List<NameValue> listNameValue;
        public Domain()
        {
            listNameValue = new List<NameValue>();
        }
    }

    class NameValue
    {
        public string name;
        public string value;
    }
}
